"""
Synthesis API endpoints for Synthese Comparative Service
"""
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, Query
import time
import uuid
from datetime import datetime
import asyncio
import re
from groq import Groq

from app.core.config import settings
from app.core.logging import get_logger
from app.services.anonymization_service import anonymization_service

router = APIRouter()
logger = get_logger(__name__)

# Initialize Groq client for AI-powered synthesis
groq_client = Groq(api_key=settings.GROQ_API_KEY) if settings.GROQ_API_KEY else None


# Helper functions for medical information extraction
def extract_symptoms(content: str) -> List[str]:
    """Extract symptoms from medical text (simplified keyword matching)"""
    symptoms = []
    symptom_keywords = [
        'fever', 'fièvre', 'cough', 'toux', 'headache', 'mal de tête', 'céphalée',
        'fatigue', 'nausea', 'nausée', 'vomiting', 'vomissement', 'pain', 'douleur',
        'shortness of breath', 'essoufflement', 'dyspnée', 'chest pain', 'douleur thoracique',
        'sore throat', 'mal de gorge', 'runny nose', 'nez qui coule', 'congestion',
        'dizziness', 'vertige', 'weakness', 'faiblesse', 'chills', 'frissons',
        'sweating', 'transpiration', 'loss of appetite', 'perte d\'appétit'
    ]
    
    for keyword in symptom_keywords:
        if keyword in content:
            # Capitalize first letter
            symptoms.append(keyword.capitalize())
    
    return list(set(symptoms))  # Remove duplicates


def extract_diagnoses(content: str) -> List[str]:
    """Extract diagnoses from medical text"""
    diagnoses = []
    diagnosis_patterns = [
        r'diagnosis:\s*([^.\n]+)',
        r'diagnostic:\s*([^.\n]+)',
        r'diagnosed with\s+([^.\n]+)',
        r'diagnostiqué\s+([^.\n]+)',
    ]
    
    diagnosis_keywords = [
        'infection', 'pneumonia', 'pneumonie', 'bronchitis', 'bronchite',
        'hypertension', 'diabetes', 'diabète', 'asthma', 'asthme',
        'covid', 'influenza', 'grippe', 'migraine', 'fracture',
        'upper respiratory tract infection', 'infection des voies respiratoires',
        'gastroenteritis', 'gastro-entérite', 'arthritis', 'arthrite'
    ]
    
    # Try pattern matching first
    for pattern in diagnosis_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        for match in matches:
            diagnoses.append(match.strip().capitalize())
    
    # Keyword matching as fallback
    for keyword in diagnosis_keywords:
        if keyword in content and keyword not in [d.lower() for d in diagnoses]:
            diagnoses.append(keyword.capitalize())
    
    return list(set(diagnoses))[:5]  # Limit to top 5


def extract_treatments(content: str) -> List[str]:
    """Extract treatments from medical text"""
    treatments = []
    treatment_patterns = [
        r'treatment:\s*([^.\n]+)',
        r'traitement:\s*([^.\n]+)',
        r'prescribed\s+([^.\n]+)',
        r'prescrit\s+([^.\n]+)',
    ]
    
    treatment_keywords = [
        'antibiotics', 'antibiotiques', 'rest', 'repos', 'hydration', 'hydratation',
        'medication', 'médicament', 'surgery', 'chirurgie', 'therapy', 'thérapie',
        'physiotherapy', 'physiothérapie', 'diet', 'régime', 'exercise', 'exercice'
    ]
    
    # Pattern matching
    for pattern in treatment_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        for match in matches:
            treatments.append(match.strip().capitalize())
    
    # Keyword matching
    for keyword in treatment_keywords:
        if keyword in content and keyword not in [t.lower() for t in treatments]:
            treatments.append(keyword.capitalize())
    
    return list(set(treatments))[:5]


def extract_medications(content: str) -> List[str]:
    """Extract medications from medical text"""
    medications = []
    med_keywords = [
        'aspirin', 'aspirine', 'ibuprofen', 'ibuprofène', 'paracetamol', 'acetaminophen',
        'amoxicillin', 'amoxicilline', 'azithromycin', 'azithromycine', 'metformin', 'metformine',
        'lisinopril', 'amlodipine', 'simvastatin', 'omeprazole', 'oméprazole',
        'insulin', 'insuline', 'morphine', 'codeine', 'codéine'
    ]
    
    for med in med_keywords:
        if med in content:
            medications.append(med.capitalize())
    
    return list(set(medications))


def extract_vital_signs(content: str) -> List[str]:
    """Extract vital signs and measurements from medical text"""
    vital_signs = []
    
    # Blood pressure
    bp_pattern = r'(\d{2,3}\/\d{2,3})\s*(mmhg|mm hg)?'
    bp_matches = re.findall(bp_pattern, content, re.IGNORECASE)
    if bp_matches:
        vital_signs.append(f"Pression artérielle: {bp_matches[0][0]} mmHg")
    
    # Temperature
    temp_pattern = r'(\d{2,3}\.?\d?)\s*°?(c|f|celsius|fahrenheit)'
    temp_matches = re.findall(temp_pattern, content, re.IGNORECASE)
    if temp_matches:
        vital_signs.append(f"Température: {temp_matches[0][0]}°{temp_matches[0][1].upper()}")
    
    # Heart rate
    hr_pattern = r'(\d{2,3})\s*(bpm|beats per minute|battements par minute)'
    hr_matches = re.findall(hr_pattern, content, re.IGNORECASE)
    if hr_matches:
        vital_signs.append(f"Fréquence cardiaque: {hr_matches[0][0]} bpm")
    
    return vital_signs


@router.post("/generate")
async def generate_synthesis(
    synthesis_request: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate structured synthesis or comparison from documents
    Uses anonymized content from database
    """
    try:
        synthesis_id = synthesis_request.get("synthesis_id")
        synthesis_type = synthesis_request.get("type")
        parameters = synthesis_request.get("parameters", {})

        logger.info(
            "Generating synthesis",
            synthesis_id=synthesis_id,
            synthesis_type=synthesis_type,
            parameters=parameters
        )

        start_time = time.time()

        # Generate synthesis result based on type with REAL anonymized data
        if synthesis_type == "patient_timeline":
            result = await generate_patient_timeline(parameters)
        elif synthesis_type == "comparison":
            result = await generate_comparison(parameters)
        elif synthesis_type == "summary":
            result = await generate_summary(parameters)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported synthesis type: {synthesis_type}"
            )

        execution_time_ms = int((time.time() - start_time) * 1000)

        response = {
            "status": "completed",
            "result": result,
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "execution_time_ms": execution_time_ms
        }

        logger.info(
            "Synthesis completed",
            synthesis_id=synthesis_id,
            synthesis_type=synthesis_type,
            execution_time_ms=execution_time_ms,
            used_anonymized_data=result.get("_metadata", {}).get("used_anonymized_data", False)
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Synthesis generation failed",
            synthesis_id=synthesis_request.get("synthesis_id"),
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Synthesis generation failed: {str(e)}"
        )


async def generate_patient_timeline(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate AI-powered patient timeline with chronological medical history
    """
    patient_id = parameters.get("patient_id", "Patient")
    document_ids = parameters.get("document_ids", [])
    
    if not document_ids:
        raise HTTPException(status_code=400, detail="Aucun document spécifié pour la chronologie")
    
    try:
        documents = await anonymization_service.get_anonymized_documents_bulk(document_ids)
        logger.info("Fetched documents for timeline", count=len(documents))
    except Exception as e:
        logger.error("Failed to fetch documents", error=str(e))
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération des documents")
    
    if not documents:
        raise HTTPException(status_code=404, detail="Aucun document trouvé")
    
    # Sort documents by date
    documents.sort(key=lambda x: x.get("created_at", ""))
    
    # Prepare timeline for AI
    doc_timeline = []
    for idx, doc in enumerate(documents, 1):
        content = doc.get("content", "")[:1500]
        date = doc.get("created_at", "Date inconnue")
        doc_timeline.append(f"**{date} - {doc['filename']}**\n{content}\n")
    
    # Generate AI timeline
    if groq_client:
        try:
            combined_docs = "\n\n---\n\n".join(doc_timeline)
            prompt = f"""Tu es un médecin expert en analyse de dossiers médicaux chronologiques.

Analyse cette chronologie médicale du patient et produis un résumé temporel professionnel en français.

CHRONOLOGIE MÉDICALE DU PATIENT:
{combined_docs}

Ta chronologie doit inclure:

1. **Résumé Chronologique** - Histoire médicale dans l'ordre temporel
2. **Évolution des Symptômes** - Progression ou amélioration
3. **Diagnostics Successifs** - Diagnostic initial et évolutions
4. **Traitements Appliqués** - Historique thérapeutique
5. **Événements Médicaux Clés** - Hospitalisations, interventions, changements majeurs
6. **État Actuel et Perspectives** - Situation actuelle et recommandations

Fournis une chronologie médicale claire et structurée."""

            response = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "Tu es un médecin expert en analyse chronologique de dossiers médicaux."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2500
            )
            
            ai_timeline = response.choices[0].message.content
            
            # Extract key findings
            key_findings = []
            for line in ai_timeline.split('\n'):
                line = line.strip()
                if line and (line.startswith('-') or line.startswith('•') or '**' in line) and len(line) < 150:
                    clean_line = line.lstrip('-•* ').replace('**', '')
                    if clean_line and len(clean_line) > 10:
                        key_findings.append(clean_line)
            
            if not key_findings:
                key_findings = ["Chronologie générée par IA", "Analyse temporelle complète"]
            
        except Exception as e:
            logger.error("Groq AI timeline failed", error=str(e))
            ai_timeline = f"**Chronologie Patient**\n\n" + "\n\n".join(doc_timeline[:3])
            key_findings = ["Chronologie basique (IA indisponible)"]
    else:
        ai_timeline = f"**Chronologie Patient**\n\n" + "\n\n".join(doc_timeline[:3])
        key_findings = ["Configuration IA requise"]
    
    sections = [
        {
            "date": doc.get("created_at", "Date inconnue"),
            "title": doc['filename'],
            "summary": doc.get("content", "")[:200] + "..."
        }
        for doc in documents
    ]

    return {
        "title": f"Chronologie Médicale - {patient_id}",
        "content": ai_timeline,
        "sections": sections,
        "key_findings": key_findings[:7],
        "_metadata": {
            "used_anonymized_data": True,
            "documents_analyzed": len(documents),
            "ai_model": "llama-3.3-70b-versatile"
        }
    }


async def generate_comparison(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate AI-powered professional medical comparison
    """
    document_ids = parameters.get("document_ids", [])
    
    # Fetch anonymized documents from database
    documents = []
    if document_ids:
        try:
            documents = await anonymization_service.get_anonymized_documents_bulk(document_ids)
            logger.info("Fetched documents for comparison", count=len(documents))
        except Exception as e:
            logger.error("Failed to fetch documents for comparison", error=str(e))
    
    if len(documents) < 2:
        raise HTTPException(status_code=400, detail="Minimum 2 documents requis pour la comparaison")
    
    # Prepare documents for AI comparison
    doc_summaries = []
    for idx, doc in enumerate(documents, 1):
        content = doc.get("content", "")[:2000]  # Limit per document
        doc_summaries.append(f"### Document {idx}: {doc['filename']}\n{content}\n")
    
    # Generate AI-powered comparison
    if groq_client:
        try:
            combined_docs = "\n\n".join(doc_summaries)
            prompt = f"""Tu es un médecin expert en analyse comparative de documents médicaux.

Compare ces {len(documents)} documents médicaux et produis une analyse comparative professionnelle en français.

DOCUMENTS À COMPARER:
{combined_docs}

Ta comparaison doit inclure:

1. **Vue d'ensemble** - Résumé de chaque document
2. **Évolution Clinique** - Progression des symptômes, diagnostics et traitements
3. **Concordances** - Points communs entre les documents
4. **Divergences** - Différences et changements notables
5. **Synthèse Médicale** - Analyse globale du dossier patient
6. **Recommandations** - Suggestions pour le suivi médical

Fournis une analyse comparative médicale structurée et professionnelle."""

            response = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "Tu es un médecin expert en analyse comparative."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2500
            )
            
            ai_comparison = response.choices[0].message.content
            
            # Extract conclusions from AI response
            conclusions = []
            in_recommendations = False
            for line in ai_comparison.split('\n'):
                line = line.strip()
                if 'recommandation' in line.lower() or 'conclusion' in line.lower():
                    in_recommendations = True
                if in_recommendations and (line.startswith('-') or line.startswith('•') or line.startswith('*')):
                    conclusions.append(line.lstrip('-•* '))
            
            if not conclusions:
                conclusions = [
                    "Analyse comparative générée par IA",
                    f"Comparaison de {len(documents)} documents médicaux",
                    "Revue médicale recommandée"
                ]
            
        except Exception as e:
            logger.error("Groq AI comparison failed", error=str(e))
            ai_comparison = f"**Comparaison de {len(documents)} documents**\n\n" + "\n\n".join(doc_summaries[:2])
            conclusions = ["Comparaison basique (IA indisponible)"]
    else:
        ai_comparison = f"**Comparaison de {len(documents)} documents**\n\n" + "\n\n".join(doc_summaries[:2])
        conclusions = ["Configuration IA requise"]
    
    comparisons = [
        {
            "document": doc['filename'],
            "size": len(doc.get('content', '')),
            "type": doc.get('file_type', 'unknown'),
            "anonymized": doc.get('is_anonymized', False)
        }
        for doc in documents
    ]

    return {
        "title": f"Analyse Comparative - {len(documents)} Documents Médicaux",
        "content": ai_comparison,
        "comparisons": comparisons,
        "conclusions": conclusions[:5],
        "_metadata": {
            "used_anonymized_data": True,
            "documents_analyzed": len(documents),
            "ai_model": "llama-3.3-70b-versatile"
        }
    }


async def generate_summary(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate AI-powered professional medical summary
    """
    patient_id = parameters.get("patient_id", "Patient")
    document_id = parameters.get("document_id")
    document_ids = parameters.get("document_ids", [])
    
    if document_id and not document_ids:
        document_ids = [document_id]
    
    if not document_ids:
        raise HTTPException(status_code=400, detail="Aucun document spécifié")
    
    try:
        document = await anonymization_service.get_anonymized_document(document_ids[0])
        if not document:
            raise ValueError(f"Document {document_ids[0]} not found")
    except Exception as e:
        logger.error("Failed to fetch document", error=str(e))
        raise HTTPException(status_code=404, detail="Document introuvable")
    
    # Get document content
    content = document.get("content", "")
    if not content or len(content.strip()) < 50:
        raise HTTPException(status_code=400, detail="Contenu du document insuffisant")
    
    # Generate AI summary with Groq
    if groq_client:
        try:
            prompt = f"""Tu es un médecin expert spécialisé dans la synthèse de documents médicaux.

Analyse ce document médical et produis une synthèse professionnelle structurée en français.

DOCUMENT À ANALYSER:
{content[:4000]}

Ta synthèse doit inclure:

1. **Informations Patient** (si disponibles)
2. **Motif de Consultation / Contexte**
3. **Antécédents Médicaux Pertinents**
4. **Symptômes et Signes Cliniques**
5. **Examens et Diagnostics**
6. **Traitement Prescrit**
7. **Recommandations et Suivi**

Fournis une synthèse médicale claire, structurée et professionnelle. Utilise un langage médical approprié mais compréhensible."""

            response = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "Tu es un médecin expert en synthèse médicale."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            ai_summary = response.choices[0].message.content
            
            # Extract summary points from AI response
            summary_points = []
            for line in ai_summary.split('\n'):
                line = line.strip()
                if line and (line.startswith('-') or line.startswith('•') or line.startswith('*')):
                    summary_points.append(line.lstrip('-•* '))
                elif line and len(line) < 100 and ':' in line:
                    summary_points.append(line)
            
            if not summary_points:
                summary_points = ["Synthèse générée par IA", "Analyse professionnelle complète"]
            
        except Exception as e:
            logger.error("Groq AI synthesis failed", error=str(e))
            ai_summary = f"**Résumé automatique**\n\nDocument: {document['filename']}\n\n{content[:800]}..."
            summary_points = ["Synthèse basique (IA indisponible)"]
    else:
        ai_summary = f"**Document médical**\n\n{content[:800]}..."
        summary_points = ["Configuration IA requise"]
    
    return {
        "title": f"Synthèse Médicale - {document['filename']}",
        "content": ai_summary,
        "summary_points": summary_points[:5],
        "recommendations": [
            "Synthèse générée par intelligence artificielle",
            "Revue médicale recommandée pour validation",
        ],
        "_metadata": {
            "used_anonymized_data": True,
            "documents_analyzed": 1,
            "is_anonymized": document.get('is_anonymized', False),
            "ai_model": "llama-3.3-70b-versatile"
        }
    }

