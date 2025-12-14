"""
DocQA-MS DeID Service
Main FastAPI application for document anonymization
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import psycopg2
import pika
import json
from datetime import datetime

from app.core.config import settings
from app.core.logging import get_logger, setup_logging

# Setup logging
setup_logging()

# Initialize FastAPI app
app = FastAPI(
    title="DocQA-MS DeID Service",
    description="Document anonymization service using Presidio and spaCy",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
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

# Pydantic models
class AnonymizationRequest(BaseModel):
    document_id: str
    content: str
    language: Optional[str] = "fr"

class AnonymizationResponse(BaseModel):
    document_id: str
    original_content: str
    anonymized_content: str
    pii_entities: List[Dict[str, Any]]
    processing_time_ms: int

class HealthResponse(BaseModel):
    status: str
    service: str
    timestamp: str
    spacy_model: str
    presidio_analyzers: List[str]

# Global variables for models (initialized lazily)
nlp = None
analyzer = None
anonymizer = None

def get_db_connection():
    """Get database connection"""
    return psycopg2.connect(settings.DATABASE_URL)

def get_rabbitmq_connection():
    """Get RabbitMQ connection"""
    connection = pika.BlockingConnection(pika.URLParameters(settings.RABBITMQ_URL))
    return connection

def initialize_models():
    """Initialize spaCy and Presidio models lazily"""
    global nlp, analyzer, anonymizer

    if nlp is None:
        try:
            import spacy
            nlp = spacy.load(settings.SPACY_MODEL)
            logger.info(f"Loaded spaCy model: {settings.SPACY_MODEL}")
        except Exception as e:
            logger.error(f"Failed to load spaCy model: {e}")
            raise

    if analyzer is None or anonymizer is None:
        try:
            from presidio_analyzer import AnalyzerEngine
            from presidio_analyzer.nlp_engine import NlpEngineProvider
            from presidio_anonymizer import AnonymizerEngine
            from app.custom_recognizers import (
                FrenchPhoneRecognizer, 
                FrenchSSNRecognizer, 
                CreditCardRecognizer,
                MedicalIDRecognizer,
                FrenchAddressRecognizer,
                DoctorNameRecognizer,
                HL7NameRecognizer,
                ArabicNameRecognizer,
                FullNameRecognizer
            )

            # Configure NLP engine for French only
            nlp_configuration = {
                "nlp_engine_name": "spacy",
                "models": [
                    {"lang_code": "fr", "model_name": settings.SPACY_MODEL}
                ]
            }
            
            nlp_engine_provider = NlpEngineProvider(nlp_configuration=nlp_configuration)
            nlp_engine = nlp_engine_provider.create_engine()

            # Create custom recognizers for French
            french_phone_recognizer = FrenchPhoneRecognizer()
            french_ssn_recognizer = FrenchSSNRecognizer()
            credit_card_recognizer = CreditCardRecognizer()
            medical_id_recognizer = MedicalIDRecognizer()
            address_recognizer = FrenchAddressRecognizer()
            doctor_name_recognizer = DoctorNameRecognizer()
            hl7_name_recognizer = HL7NameRecognizer()
            arabic_name_recognizer = ArabicNameRecognizer()
            full_name_recognizer = FullNameRecognizer()

            # Initialize analyzer with French NLP support and custom recognizers
            analyzer = AnalyzerEngine(
                nlp_engine=nlp_engine,
                supported_languages=["fr"],
                registry=None  # Use default registry
            )
            
            # Add custom recognizers
            analyzer.registry.add_recognizer(french_phone_recognizer)
            analyzer.registry.add_recognizer(french_ssn_recognizer)
            analyzer.registry.add_recognizer(credit_card_recognizer)
            analyzer.registry.add_recognizer(medical_id_recognizer)
            analyzer.registry.add_recognizer(address_recognizer)
            analyzer.registry.add_recognizer(doctor_name_recognizer)
            analyzer.registry.add_recognizer(hl7_name_recognizer)
            analyzer.registry.add_recognizer(arabic_name_recognizer)
            analyzer.registry.add_recognizer(full_name_recognizer)
            
            anonymizer = AnonymizerEngine()

            logger.info("Initialized Presidio analyzer and anonymizer with French support and custom recognizers")
        except Exception as e:
            logger.error(f"Failed to initialize Presidio: {e}")
            raise

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        # Test spaCy model
        spacy_status = "loaded" if nlp else "not_loaded"

        return HealthResponse(
            status="healthy",
            service="deid",
            timestamp=datetime.utcnow().isoformat(),
            spacy_model=settings.SPACY_MODEL,
            presidio_analyzers=settings.PRESIDIO_ANALYZERS
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

@app.post("/anonymize", response_model=AnonymizationResponse)
async def anonymize_document(request: AnonymizationRequest):
    """
    Anonymize a document by removing or replacing PII
    """
    start_time = datetime.utcnow()

    try:
        # Initialize models if needed
        initialize_models()

        # Analyze the text for PII using spaCy NER with explicit entity types
        try:
            analyzer_results = analyzer.analyze(
                text=request.content,
                language=request.language,
                score_threshold=0.4,  # Balanced threshold - not too low to avoid medical terms
                entities=[
                    "PERSON", "DATE_TIME", "LOCATION", "ADDRESS", 
                    "PHONE_NUMBER", "EMAIL_ADDRESS", "IBAN_CODE",
                    "CREDIT_CARD", "MEDICAL_ID", "NRP", "IP_ADDRESS",
                    "URL", "AGE", "ID"
                ]
            )
            
            # Filter out false positives (field labels and common medical terms)
            # These are NOT PII - they are medical terminology and field labels
            false_positive_patterns = [
                # Field labels
                "numero", "numéro", "nom", "prenom", "prénom", "adresse", 
                "telephone", "téléphone", "email", "date", "sexe", "âge", "age",
                
                # Gender terms
                "masculin", "féminin", "feminin", "homme", "femme", "male", "female",
                
                # Vital signs and measurements
                "température", "temperature", "pression", "fréquence", "frequence",
                "poids", "taille", "imc", "saturation", "glycémie", "glycemie",
                
                # Medical personnel (general terms, not names)
                "patient", "patiente", "medecin", "médecin", "infirmier", "infirmière",
                
                # Medical terms and diagnoses
                "diagnostic", "traitement", "prescription", "ordonnance",
                "consultation", "examen", "analyse", "resultats", "résultats",
                "symptomes", "symptômes", "douleur", "fievre", "fièvre",
                
                # Common diseases and conditions  
                "hypertension", "diabete", "diabète", "cholesterol", "cholestérol",
                "infection", "inflammation", "fracture", "entorse",
                "cystite", "pyélonéphrite", "pyelonephrite", "angine", "grippe",
                "bronchite", "pneumonie", "asthme", "allergie",
                
                # Body parts and systems
                "cardiaque", "pulmonaire", "hepatique", "hépatique", 
                "renale", "rénale", "renal", "cerebral", "cérébral",
                "arterielle", "artérielle", "arteriel", "artériel",
                "lombaire", "thoracique", "abdominale", "abdominal",
                
                # Medical specialties and types
                "clinique", "medical", "médical", "chirurgical", "therapeutique", "thérapeutique",
                "aigu", "aiguë", "chronique", "complique", "compliqué", "compliquee", "compliquée",
                
                # Lab results and bacteria
                "bacterie", "bactérie", "virus", "coli", "escherichia", "escherichia coli", "e. coli",
                "staphylocoque", "streptocoque", "leucocytes", "nitrites", "ecbu", "crp", 
                "elevee", "élevée", "eleve", "élevé", "isole", "isolé", "isolee", "isolée",
                
                # Medications and treatments  
                "antibiotique", "paracetamol", "ciprofloxacine", "amoxicilline",
                "ibuprofene", "ibuprofène", "aspirine", "doliprane",
                
                # Administrative terms
                "rapport", "dossier", "hopital", "hôpital", "service", "urgence",
                "rendez-vous", "hospitalisation", "suivi"
            ]
            
            filtered_results = []
            for result in analyzer_results:
                entity_text = request.content[result.start:result.end].strip()
                entity_text_lower = entity_text.lower()
                
                # Skip if it's just a field label (short word matching our list)
                if entity_text_lower in false_positive_patterns:
                    logger.info(f"Skipping false positive: {entity_text} (type: {result.entity_type})")
                    continue
                
                # Exception: Don't skip if it's a doctor name (contains Dr., Docteur, Pr.)
                is_doctor_name = any(title in entity_text for title in ["Dr.", "Dr ", "Docteur", "Pr.", "Professeur"])
                
                # Skip if it contains common medical terms (partial match)
                # This catches compound terms like "Pyélonéphrite aiguë"
                # BUT don't skip doctor names
                is_medical_term = False
                if not is_doctor_name:
                    for medical_term in false_positive_patterns:
                        if len(medical_term) > 4 and medical_term in entity_text_lower:
                            logger.info(f"Skipping medical term: {entity_text} (contains '{medical_term}', type: {result.entity_type})")
                            is_medical_term = True
                            break
                
                if is_medical_term:
                    continue
                
                # Skip very short entities (likely false positives) unless high confidence
                if len(entity_text) < 3 and result.score < 0.9:
                    continue
                
                # Skip entities that look like measurements (number + unit)
                import re
                if re.match(r'^\d+[\s]*(mg|g|kg|ml|l|°c|mmhg|bpm|%)', entity_text_lower):
                    logger.info(f"Skipping measurement: {entity_text}")
                    continue
                    
                filtered_results.append(result)
            
            analyzer_results = filtered_results
            
        except Exception as analyze_error:
            logger.error(f"Error during PII analysis: {analyze_error}")
            # If analysis fails, still return the original content with a warning
            return AnonymizationResponse(
                document_id=request.document_id,
                original_content=request.content,
                anonymized_content=request.content,
                pii_entities=[],
                processing_time_ms=int((datetime.utcnow() - start_time).total_seconds() * 1000)
            )

        # Log the analysis results for debugging
        logger.info(f"Found {len(analyzer_results)} PII entities in document {request.document_id}")
        for result in analyzer_results:
            logger.info(f"Entity: {result.entity_type}, Score: {result.score}")

        # Convert analyzer results to dict format
        pii_entities = []
        for result in analyzer_results:
            pii_entities.append({
                "entity_type": result.entity_type,
                "start": result.start,
                "end": result.end,
                "confidence_score": result.score,
                "text": request.content[result.start:result.end]
            })

        # Anonymize the text
        anonymized_result = anonymizer.anonymize(
            text=request.content,
            analyzer_results=analyzer_results
        )

        # Calculate processing time
        processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)

        # Save anonymization results to database
        await save_anonymization_result(
            document_id=request.document_id,
            original_content=request.content,
            anonymized_content=anonymized_result.text,
            pii_entities=pii_entities,
            processing_time=processing_time
        )

        return AnonymizationResponse(
            document_id=request.document_id,
            original_content=request.content,
            anonymized_content=anonymized_result.text,
            pii_entities=pii_entities,
            processing_time_ms=processing_time
        )

    except Exception as e:
        logger.error(f"Error anonymizing document {request.document_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Anonymization failed: {str(e)}")

@app.get("/anonymize/status/{document_id}")
async def get_anonymization_status(document_id: str):
    """Get anonymization status for a document"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT original_content, anonymized_content, pii_entities,
                   processing_time_ms, created_at
            FROM document_anonymizations
            WHERE document_id = %s
            ORDER BY created_at DESC
            LIMIT 1
        """, (document_id,))

        row = cursor.fetchone()
        cursor.close()
        conn.close()

        if row:
            return {
                "document_id": document_id,
                "status": "completed",
                "original_length": len(row[0]),
                "anonymized_length": len(row[1]),
                "pii_entities_count": len(row[2]) if row[2] else 0,
                "processing_time_ms": row[3],
                "processed_at": row[4].isoformat()
            }
        else:
            return {
                "document_id": document_id,
                "status": "not_found"
            }

    except Exception as e:
        logger.error(f"Error getting anonymization status for {document_id}: {e}")
        raise HTTPException(status_code=500, detail="Database error")

async def save_anonymization_result(
    document_id: str,
    original_content: str,
    anonymized_content: str,
    pii_entities: List[Dict[str, Any]],
    processing_time: int
):
    """Save anonymization result to database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO document_anonymizations (
                document_id, original_content, anonymized_content,
                pii_entities, processing_time_ms
            ) VALUES (%s, %s, %s, %s, %s)
        """, (
            document_id,
            original_content,
            anonymized_content,
            json.dumps(pii_entities) if pii_entities else None,
            processing_time
        ))

        conn.commit()
        cursor.close()
        conn.close()

        logger.info(f"Saved anonymization result for document {document_id}")

    except Exception as e:
        logger.error(f"Error saving anonymization result: {e}")
        # Don't raise exception - anonymization worked, just logging failed

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)