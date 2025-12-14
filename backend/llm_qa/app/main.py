"""
DocQA-MS LLM QA Service
Main FastAPI application for question-answering using Groq API
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import httpx
import psycopg2
import pika
from groq import Groq
import json
import uuid
from datetime import datetime

from app.core.config import settings
from app.core.logging import get_logger, setup_logging
from app.core.database import db_manager

# Setup logging
setup_logging()

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting LLM Q&A service")
    
    # Initialize database connection
    try:
        await db_manager.connect()
        logger.info("Database connection established")
    except Exception as e:
        logger.error("Failed to connect to database", error=str(e))

    yield

    # Shutdown
    logger.info("Shutting down LLM Q&A service")
    await db_manager.disconnect()


# Initialize FastAPI app
app = FastAPI(
    title="DocQA-MS LLM QA Service",
    description="Question-Answering service using Groq API for medical documents",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = get_logger(__name__)

# Initialize Groq client
groq_client = Groq(api_key=settings.GROQ_API_KEY)

# Pydantic models
class QARequest(BaseModel):
    question: str
    context_documents: List[str] = []  # Document IDs
    session_id: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 1000

class QAResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    confidence_score: float
    execution_time_ms: int
    model_used: str
    tokens_used: int

class DocumentChunk(BaseModel):
    id: str
    document_id: str
    content: str
    metadata: Dict[str, Any]

# Database connection
def get_db_connection():
    """Get database connection"""
    return psycopg2.connect(settings.DATABASE_URL)

# RabbitMQ connection
def get_rabbitmq_connection():
    """Get RabbitMQ connection"""
    connection = pika.BlockingConnection(pika.URLParameters(settings.RABBITMQ_URL))
    return connection

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "llm-qa",
        "timestamp": datetime.utcnow().isoformat(),
        "groq_api": "configured" if settings.GROQ_API_KEY else "not_configured"
    }

@app.post("/qa/ask", response_model=QAResponse)
async def ask_question(request: QARequest):
    """
    Answer a question using Groq API with context from medical documents
    """
    start_time = datetime.utcnow()

    try:
        # Step 1: Search for relevant document chunks using semantic search
        relevant_chunks = await search_relevant_chunks(
            request.question, 
            document_ids=request.context_documents if request.context_documents else None,
            limit=5
        )
        
        if not relevant_chunks:
            logger.warning("No relevant document chunks found for question")
            raise HTTPException(
                status_code=404,
                detail="No relevant documents found to answer this question. Please ensure documents are indexed."
            )

        # Step 2: Prepare context for LLM
        context_text = prepare_context(relevant_chunks)

        # Step 3: Create prompt for medical Q&A
        prompt = create_medical_qa_prompt(request.question, context_text)

        # Step 4: Call Groq API with fallback models (updated to current models)
        models_to_try = [
            "llama-3.3-70b-versatile",  # Latest Llama 3.3
            "llama-3.1-8b-instant",     # Fast Llama 3.1
            "mixtral-8x7b-32768",       # Mixtral fallback
            "gemma2-9b-it"              # Gemma fallback
        ]

        response = None
        last_error = None
        model_used = None

        for model in models_to_try:
            try:
                response = groq_client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "system", 
                            "content": """Tu es un assistant médical IA hautement spécialisé, conçu pour aider les professionnels de santé dans l'analyse de documents cliniques. 

Tes compétences clés:
- Analyse approfondie de dossiers médicaux en français
- Extraction d'informations cliniques précises
- Synthèse de données médicales complexes
- Respect absolu de la confidentialité et de l'éthique médicale

Tes principes fondamentaux:
1. PRÉCISION: Base tes réponses exclusivement sur les documents fournis
2. TRAÇABILITÉ: Cite tes sources en mentionnant "Source: Document médical" sans révéler d'identifiants techniques
3. HONNÊTETÉ: Admets clairement quand l'information n'est pas disponible
4. CLARTÉ: Structure tes réponses de manière professionnelle et lisible
5. SÉCURITÉ: Ne donne jamais de conseils médicaux non fondés sur les documents

Tu travailles avec des documents qui peuvent contenir des données anonymisées (marquées <PERSON>, <LOCATION>, <DATE_TIME>, etc.) pour protéger la vie privée des patients.

IMPORTANT: Dans tes réponses, ne mentionne JAMAIS les identifiants techniques de documents (UUIDs). Réfère-toi simplement au "document source" ou "dossier médical"."""
                        },
                        {"role": "user", "content": prompt}
                    ],
                    temperature=request.temperature,
                    max_tokens=request.max_tokens,
                )
                model_used = model
                logger.info(f"Successfully used model: {model}")
                break
            except Exception as e:
                last_error = str(e)
                logger.warning(f"Model {model} failed: {e}")
                continue

        if response is None:
            logger.error(f"All Groq models failed. Last error: {last_error}")
            raise HTTPException(
                status_code=503,
                detail=f"LLM service unavailable. Please check Groq API configuration. Error: {last_error}"
            )

        answer = response.choices[0].message.content
        tokens_used = response.usage.total_tokens

        # Calculate execution time
        execution_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)

        # Extract sources from context
        sources = extract_sources(relevant_chunks, answer)

        # Calculate confidence score
        confidence_score = calculate_confidence_score(answer, context_text)

        # Save Q&A interaction to database
        await save_qa_interaction(
            question=request.question,
            answer=answer,
            sources=sources,
            confidence_score=confidence_score,
            execution_time=execution_time,
            tokens_used=tokens_used,
            session_id=request.session_id
        )

        return QAResponse(
            answer=answer,
            sources=sources,
            confidence_score=confidence_score,
            execution_time_ms=execution_time,
            model_used=model_used or "unknown",
            tokens_used=tokens_used
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error processing Q&A request", error=str(e))
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

async def get_document_chunks(document_ids: List[str]) -> List[DocumentChunk]:
    """Retrieve document chunks from database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get chunks for specified documents
        placeholders = ','.join(['%s'] * len(document_ids))
        query = f"""
        SELECT id, document_id, content, metadata
        FROM document_chunks
        WHERE document_id IN ({placeholders})
        ORDER BY document_id, chunk_index
        """

        cursor.execute(query, document_ids)
        rows = cursor.fetchall()

        chunks = []
        for row in rows:
            chunks.append(DocumentChunk(
                id=str(row[0]),
                document_id=str(row[1]),
                content=row[2],
                metadata=row[3] if row[3] else {}
            ))

        cursor.close()
        conn.close()

        return chunks

    except Exception as e:
        logger.error("Error retrieving document chunks", error=str(e))
        return []


async def search_relevant_chunks(question: str, document_ids: List[str] = None, limit: int = 5) -> List[DocumentChunk]:
    """Search for relevant document chunks using semantic search"""
    try:
        logger.info(f"Searching for relevant chunks for question: {question[:100]}")
        
        # When filtering by documents, increase search limit to ensure we get results from all selected docs
        # (FAISS returns results before filtering, so we need to over-fetch)
        search_limit = limit * 3 if document_ids and len(document_ids) > 1 else limit
        
        # Prepare search request payload
        search_payload = {
            "query": question,
            "limit": search_limit,
            "threshold": 0.3,  # Minimum relevance score
            "filters": {}
        }
        
        # Add document_ids filter if specified
        if document_ids and len(document_ids) > 0:
            search_payload["filters"]["document_ids"] = document_ids
            logger.info(f"Filtering search to {len(document_ids)} specific documents")
        
        # Call the indexer's search endpoint
        async with httpx.AsyncClient(timeout=30.0) as client:
            search_response = await client.post(
                f"{settings.INDEXER_URL}/api/v1/search/",
                json=search_payload
            )
            
            if search_response.status_code != 200:
                logger.error(f"Search service failed with status {search_response.status_code}")
                return []
            
            search_results = search_response.json()
            results = search_results.get("results", [])
            
            # Log what the search API returned
            logger.info(f"Search API returned {len(results)} results")
            if results:
                doc_ids = [r.get("document_id", "unknown") for r in results]
                logger.info(f"Document IDs in search results: {doc_ids}")
            
            if not results:
                logger.warning("No search results found")
                return []
            
            # Convert search results to DocumentChunk objects
            chunks = []
            for result in results:
                chunks.append(DocumentChunk(
                    id=result.get("chunk_id", str(uuid.uuid4())),
                    document_id=result.get("document_id", "unknown"),
                    content=result.get("text", result.get("content", "")),
                    metadata={
                        "score": result.get("score", 0.0),
                        "chunk_index": result.get("chunk_index", 0),
                        "filename": result.get("filename", None),  # Preserve filename from search results
                        "file_type": result.get("file_type", None)  # Preserve file type
                    }
                ))
            
            logger.info(f"Found {len(chunks)} relevant chunks")
            return chunks
            
    except httpx.RequestError as e:
        logger.error(f"Failed to connect to search service: {e}")
        return []
    except Exception as e:
        logger.error(f"Error searching for relevant chunks: {e}")
        return []

def prepare_context(chunks: List[DocumentChunk]) -> str:
    """Prepare context text from document chunks"""
    if not chunks:
        return "No specific document context provided."

    context_parts = []
    for chunk in chunks[:5]:  # Limit to top 5 chunks to avoid token limits
        context_parts.append(f"[Document {chunk.document_id}]: {chunk.content}")

    return "\n\n".join(context_parts)

def create_medical_qa_prompt(question: str, context: str) -> str:
    """Create an advanced medical Q&A prompt with sophisticated prompt engineering"""
    return f"""Tu es un assistant médical expert spécialisé dans l'analyse de documents cliniques français. Ta mission est de fournir des réponses précises, factuelles et basées uniquement sur les documents fournis.

## DOCUMENTS MÉDICAUX DISPONIBLES
{context}

## QUESTION DU PROFESSIONNEL DE SANTÉ
{question}

## INSTRUCTIONS DÉTAILLÉES POUR LA RÉPONSE

### 1. ANALYSE ET COMPRÉHENSION
- Lis attentivement tous les documents fournis
- Identifie les informations pertinentes pour répondre à la question
- Note les contradictions ou informations manquantes

### 2. STRUCTURE DE LA RÉPONSE
Ta réponse doit suivre ce format structuré :

**Réponse Directe:**
- Commence par une réponse claire et concise (2-3 phrases maximum)
- Utilise un langage médical approprié mais compréhensible

**Preuves Documentaires:**
- Cite les passages spécifiques des documents qui soutiennent ta réponse
- Indique l'ID du document pour chaque citation
- Utilise des citations directes quand c'est pertinent

**Contexte Clinique:**
- Fournis le contexte médical additionnel si nécessaire
- Explique les implications cliniques
- Mentionne les facteurs importants à considérer

**Niveau de Confiance:**
- Indique ton niveau de confiance : Élevé / Moyen / Faible
- Justifie ce niveau basé sur la qualité et quantité d'informations disponibles

### 3. RÈGLES STRICTES À RESPECTER
✓ Réponds UNIQUEMENT avec les informations des documents fournis
✓ Si l'information n'est pas dans les documents, dis clairement "L'information n'est pas disponible dans les documents fournis"
✓ Ne fais JAMAIS d'inventions ou d'hypothèses non fondées
✓ Cite systématiquement tes sources (ID du document)
✓ Utilise la terminologie médicale française correcte
✓ Sois précis avec les valeurs numériques, dates, et dosages
✓ Identifie les informations anonymisées (ex: <PERSON>, <DATE_TIME>) et mentionne que certaines données sont masquées pour confidentialité

✗ N'invente pas d'informations
✗ Ne fais pas de diagnostics ou recommandations thérapeutiques non présents dans les documents
✗ N'utilise pas de connaissances externes non vérifiables dans les documents
✗ Ne donne pas d'avis personnel ou de conseil médical générique

### 4. GESTION DES CAS PARTICULIERS
- **Information partielle**: Si seulement une partie de la réponse est disponible, indique clairement ce qui est connu et ce qui manque
- **Informations contradictoires**: Signale les contradictions et présente les deux versions avec leurs sources
- **Données anonymisées**: Mentionne que certaines données personnelles sont masquées (ex: noms, dates)
- **Absence d'information**: Si aucune information pertinente n'est trouvée, suggère quels types de documents seraient nécessaires

### 5. QUALITÉ DE LA RÉPONSE
- Sois factuel et objectif
- Utilise des bullet points pour la clarté
- Inclus les unités de mesure appropriées
- Vérifie la cohérence temporelle des informations
- Priorise les informations les plus récentes si dates disponibles

Maintenant, réponds à la question en suivant rigoureusement ces instructions."""

def extract_sources(chunks: List[DocumentChunk], answer: str) -> List[Dict[str, Any]]:
    """Extract source references from answer"""
    sources = []
    for chunk in chunks:
        # All chunks that were used for search are relevant sources
        sources.append({
            "document_id": chunk.document_id,
            "chunk_id": chunk.id,
            "relevance_score": chunk.metadata.get('score', 0.8) if chunk.metadata else 0.8,
            "content": chunk.content,  # Changed from excerpt to content
            "filename": chunk.metadata.get('filename', f"Document {chunk.document_id[:8]}")  # Add filename if available
        })

    return sources  # Return all sources that were found

def calculate_confidence_score(answer: str, context: str) -> float:
    """Calculate confidence score (simplified)"""
    # Basic confidence calculation
    if len(answer.strip()) < 50:
        return 0.3  # Too short answer
    if len(context.strip()) < 100:
        return 0.4  # Limited context

    # Check for medical terminology
    medical_terms = ["traitement", "diagnostic", "patient", "médical", "clinique", "prescription"]
    term_count = sum(1 for term in medical_terms if term in answer.lower())

    base_confidence = 0.6
    confidence = base_confidence + (term_count * 0.1)

    return min(confidence, 0.95)  # Cap at 95%

async def save_qa_interaction(
    question: str,
    answer: str,
    sources: List[Dict[str, Any]],
    confidence_score: float,
    execution_time: int,
    tokens_used: int,
    session_id: Optional[str] = None
):
    """Save Q&A interaction to database"""
    try:
        # NOTE: The API Gateway is responsible for recording QA interactions
        # and audit logs in the central database. To avoid duplicate entries
        # we don't persist interactions here in the LLM service. This function
        # remains as a hook for local logging and future extensibility.
        logger.info(
            "Q&A interaction (llm_qa) processed - not saved to central DB",
            session_id=session_id,
            question_length=len(question),
            answer_length=len(answer),
            sources_count=len(sources) if sources else 0,
        )

        # Return a placeholder interaction id for compatibility if needed
        return None
    except Exception as e:
        logger.error("Error saving Q&A interaction", error=str(e))
        # Don't raise exception - Q&A should still work even if logging fails

@app.get("/qa/sessions")
async def get_qa_sessions():
    """Get user's Q&A sessions"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, session_title, created_at, updated_at
            FROM qa_sessions
            ORDER BY updated_at DESC
            LIMIT 20
        """)

        sessions = []
        for row in cursor.fetchall():
            sessions.append({
                "id": str(row[0]),
                "title": row[1],
                "created_at": row[2].isoformat() if row[2] else None,
                "updated_at": row[3].isoformat() if row[3] else None
            })

        cursor.close()
        conn.close()

        return {"sessions": sessions}

    except Exception as e:
        logger.error("Error retrieving Q&A sessions", error=str(e))
        raise HTTPException(status_code=500, detail="Error retrieving sessions")

@app.get("/qa/sessions/{session_id}")
async def get_session_interactions(session_id: str):
    """Get conversation history for a session"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT user_query, llm_response, response_sources,
                   confidence_score, execution_time_ms, created_at
            FROM qa_interactions
            WHERE session_id = %s
            ORDER BY created_at ASC
        """, (session_id,))

        interactions = []
        for row in cursor.fetchall():
            interactions.append({
                "question": row[0],
                "answer": row[1],
                "sources": row[2] if row[2] else [],
                "confidence_score": float(row[3]) if row[3] else 0.0,
                "execution_time_ms": row[4],
                "timestamp": row[5].isoformat() if row[5] else None
            })

        cursor.close()
        conn.close()

        return {"session_id": session_id, "interactions": interactions}

    except Exception as e:
        logger.error("Error retrieving session interactions", error=str(e))
        raise HTTPException(status_code=500, detail="Error retrieving interactions")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)