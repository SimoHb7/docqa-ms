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

from app.core.config import settings
from app.core.logging import get_logger
from app.services.anonymization_service import anonymization_service

router = APIRouter()
logger = get_logger(__name__)


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
    Generate patient timeline synthesis using REAL anonymized documents
    """
    patient_id = parameters.get("patient_id", "ANON_PAT_001")
    document_ids = parameters.get("document_ids", [])
    
    # Fetch anonymized documents from database
    documents = []
    if document_ids:
        try:
            documents = await anonymization_service.get_anonymized_documents_bulk(document_ids)
            logger.info("Fetched documents for timeline", count=len(documents))
        except Exception as e:
            logger.error("Failed to fetch documents for timeline", error=str(e))
            # Continue with empty documents list
    
    # Extract timeline data
    timeline_data = await anonymization_service.extract_patient_timeline_data(documents)
    
    # Generate timeline content from real documents
    sections = []
    key_findings = []
    
    if documents:
        # Build timeline from actual document content
        content_parts = [f"# Chronologie du patient {patient_id}\n\n## Documents analysés\n"]
        
        for idx, doc in enumerate(documents, 1):
            doc_date = doc.get("created_at", "Date inconnue")
            content_parts.append(f"### Document {idx}: {doc['filename']}")
            content_parts.append(f"- **Date**: {doc_date}")
            content_parts.append(f"- **Type**: {doc.get('file_type', 'unknown')}")
            content_parts.append(f"- **Anonymisé**: {'Oui' if doc.get('is_anonymized') else 'Non'}")
            
            # Extract first 300 characters as preview
            content_preview = doc.get("content", "")[:300]
            if content_preview:
                content_parts.append(f"- **Extrait**: {content_preview}...\n")
            
            # Add to sections
            sections.append({
                "title": doc['filename'],
                "content": content_preview,
                "date": doc_date
            })
            
            # Extract key findings (simplified - would use NLP in production)
            if "hypertension" in doc.get("content", "").lower():
                key_findings.append("Hypertension détectée")
            if "diabète" in doc.get("content", "").lower() or "diabetes" in doc.get("content", "").lower():
                key_findings.append("Diabète mentionné")
        
        content = "\n".join(content_parts)
    else:
        # Fallback content if no documents provided
        content = f"""# Chronologie du patient {patient_id}

## Aucun document fourni

Veuillez spécifier des document_ids dans les paramètres pour générer une chronologie basée sur les documents réels.
"""
        logger.warning("No documents provided for timeline generation")

    return {
        "title": f"Chronologie du patient {patient_id}",
        "content": content,
        "sections": sections,
        "key_findings": key_findings if key_findings else ["Analyse basée sur documents réels"],
        "_metadata": {
            "used_anonymized_data": True,
            "documents_analyzed": len(documents),
            "total_pii_detected": sum(doc.get("pii_count", 0) for doc in timeline_data["documents"]),
        }
    }


async def generate_comparison(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate comparison synthesis using REAL anonymized documents
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
        logger.warning("Comparison requires at least 2 documents", provided=len(documents))
        return {
            "title": "Comparaison inter-documents",
            "content": "⚠️ La comparaison nécessite au moins 2 documents. Veuillez fournir plusieurs document_ids.",
            "comparisons": [],
            "conclusions": ["Nombre de documents insuffisant pour la comparaison"],
            "_metadata": {
                "used_anonymized_data": True,
                "documents_analyzed": len(documents),
                "error": "Insufficient documents"
            }
        }
    
    # Extract comparison data
    comparison_data = await anonymization_service.extract_comparison_data(documents)
    
    # Build comparison content from real documents
    content_parts = [f"# Comparaison médicale entre {len(documents)} documents\n"]
    comparisons = []
    
    # Extract medical information from each document
    medical_info = []
    for idx, doc in enumerate(documents, 1):
        content = doc.get("content", "").lower()
        
        # Extract medical entities (simplified - production would use NLP/NER)
        info = {
            "doc_num": idx,
            "filename": doc['filename'],
            "symptoms": extract_symptoms(content),
            "diagnoses": extract_diagnoses(content),
            "treatments": extract_treatments(content),
            "medications": extract_medications(content),
            "vital_signs": extract_vital_signs(content),
        }
        medical_info.append(info)
        
        # Add document header
        label = f"Document {idx}"
        content_parts.append(f"\n## {label}: {doc['filename']}")
        content_parts.append(f"- **Type**: {doc.get('file_type', 'unknown')}")
        content_parts.append(f"- **Anonymisé**: {'Oui' if doc.get('is_anonymized') else 'Non'}")
        content_parts.append(f"- **Taille**: {len(doc.get('content', ''))} caractères\n")
        
        # Add extracted medical content
        if info["symptoms"]:
            content_parts.append(f"### Symptômes détectés:")
            for symptom in info["symptoms"]:
                content_parts.append(f"  - {symptom}")
        
        if info["diagnoses"]:
            content_parts.append(f"\n### Diagnostics:")
            for diagnosis in info["diagnoses"]:
                content_parts.append(f"  - {diagnosis}")
        
        if info["treatments"]:
            content_parts.append(f"\n### Traitements:")
            for treatment in info["treatments"]:
                content_parts.append(f"  - {treatment}")
        
        if info["medications"]:
            content_parts.append(f"\n### Médicaments:")
            for med in info["medications"]:
                content_parts.append(f"  - {med}")
        
        if info["vital_signs"]:
            content_parts.append(f"\n### Signes vitaux:")
            for sign in info["vital_signs"]:
                content_parts.append(f"  - {sign}")
        
        # Build comparison entry
        comparisons.append({
            "category": f"Document {idx}",
            "filename": doc['filename'],
            "size": len(doc.get('content', '')),
            "is_anonymized": doc.get('is_anonymized', False),
            "pii_count": len(doc.get('pii_entities', [])),
            "symptoms_count": len(info["symptoms"]),
            "diagnoses_count": len(info["diagnoses"]),
            "treatments_count": len(info["treatments"]),
        })
    
    # Add comparative analysis
    content_parts.append("\n## 🔍 Analyse comparative médicale\n")
    
    # Compare symptoms across documents
    all_symptoms = set()
    for info in medical_info:
        all_symptoms.update(info["symptoms"])
    if all_symptoms:
        content_parts.append("### Symptômes communs et différences:")
        for symptom in all_symptoms:
            docs_with_symptom = [info["doc_num"] for info in medical_info if symptom in info["symptoms"]]
            if len(docs_with_symptom) > 1:
                content_parts.append(f"  - ✓ **{symptom}** (Documents: {', '.join(map(str, docs_with_symptom))})")
            else:
                content_parts.append(f"  - {symptom} (Document {docs_with_symptom[0]} uniquement)")
    
    # Compare diagnoses
    all_diagnoses = set()
    for info in medical_info:
        all_diagnoses.update(info["diagnoses"])
    if all_diagnoses:
        content_parts.append("\n### Diagnostics comparés:")
        for diagnosis in all_diagnoses:
            docs_with_diagnosis = [info["doc_num"] for info in medical_info if diagnosis in info["diagnoses"]]
            if len(docs_with_diagnosis) > 1:
                content_parts.append(f"  - ✓ **{diagnosis}** (Documents: {', '.join(map(str, docs_with_diagnosis))})")
            else:
                content_parts.append(f"  - {diagnosis} (Document {docs_with_diagnosis[0]} uniquement)")
    
    # Compare treatments
    all_treatments = set()
    for info in medical_info:
        all_treatments.update(info["treatments"])
    if all_treatments:
        content_parts.append("\n### Traitements comparés:")
        for treatment in all_treatments:
            docs_with_treatment = [info["doc_num"] for info in medical_info if treatment in info["treatments"]]
            if len(docs_with_treatment) > 1:
                content_parts.append(f"  - ✓ **{treatment}** (Documents: {', '.join(map(str, docs_with_treatment))})")
            else:
                content_parts.append(f"  - {treatment} (Document {docs_with_treatment[0]} uniquement)")
    
    # Add technical metadata
    content_parts.append("\n## 📊 Métadonnées techniques\n")
    lengths = [len(doc.get('content', '')) for doc in documents]
    content_parts.append(f"- **Document le plus long**: Document {lengths.index(max(lengths)) + 1} ({max(lengths)} caractères)")
    content_parts.append(f"- **Document le plus court**: Document {lengths.index(min(lengths)) + 1} ({min(lengths)} caractères)")
    
    # Compare anonymization
    anonymized_count = sum(1 for doc in documents if doc.get('is_anonymized'))
    content_parts.append(f"- **Documents anonymisés**: {anonymized_count}/{len(documents)}")
    
    # Compare PII detection
    total_pii = sum(len(doc.get('pii_entities', [])) for doc in documents)
    content_parts.append(f"- **Total d'entités PII détectées**: {total_pii}")
    
    content = "\n".join(content_parts)
    
    # Generate smart conclusions
    conclusions = []
    
    # Symptom analysis
    total_symptoms = sum(len(info["symptoms"]) for info in medical_info)
    if total_symptoms > 0:
        conclusions.append(f"{total_symptoms} symptôme(s) identifié(s) au total")
    
    # Diagnosis analysis
    total_diagnoses = sum(len(info["diagnoses"]) for info in medical_info)
    if total_diagnoses > 0:
        conclusions.append(f"{total_diagnoses} diagnostic(s) mentionné(s)")
    
    # Common findings
    common_symptoms = [s for s in all_symptoms if sum(1 for info in medical_info if s in info["symptoms"]) > 1]
    if common_symptoms:
        conclusions.append(f"Symptômes communs trouvés: {', '.join(list(common_symptoms)[:3])}")
    
    conclusions.append(f"{anonymized_count} document(s) anonymisé(s) sur {len(documents)}")

    return {
        "title": f"Comparaison médicale - {len(documents)} documents",
        "content": content,
        "comparisons": comparisons,
        "conclusions": conclusions,
        "_metadata": {
            "used_anonymized_data": True,
            "documents_analyzed": len(documents),
            "total_pii_detected": total_pii,
        }
    }


async def generate_summary(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate summary synthesis using REAL anonymized document
    """
    patient_id = parameters.get("patient_id", "ANON_PAT_001")
    document_id = parameters.get("document_id")
    document_ids = parameters.get("document_ids", [])
    
    # Handle both single document_id and document_ids array
    if document_id and not document_ids:
        document_ids = [document_id]
    
    if not document_ids:
        logger.warning("No document ID provided for summary")
        return {
            "title": f"Synthèse médicale - {patient_id}",
            "content": "⚠️ Aucun document spécifié. Veuillez fournir un document_id ou document_ids.",
            "summary_points": ["Aucun document à résumer"],
            "recommendations": ["Fournir un document_id valide"],
            "_metadata": {
                "used_anonymized_data": False,
                "documents_analyzed": 0,
                "error": "No document ID provided"
            }
        }
    
    # Fetch the first document (summary is typically for single document)
    try:
        document = await anonymization_service.get_anonymized_document(document_ids[0])
        if not document:
            raise ValueError(f"Document {document_ids[0]} not found")
    except Exception as e:
        logger.error("Failed to fetch document for summary", error=str(e))
        return {
            "title": f"Synthèse médicale - {patient_id}",
            "content": f"❌ Erreur: Impossible de récupérer le document {document_ids[0]}",
            "summary_points": ["Document introuvable"],
            "recommendations": ["Vérifier l'ID du document"],
            "_metadata": {
                "used_anonymized_data": False,
                "documents_analyzed": 0,
                "error": str(e)
            }
        }
    
    # Extract summary data
    summary_data = await anonymization_service.extract_summary_data(document)
    
    # Generate summary from real document
    content_preview = document["content"][:500] if document.get("content") else "Contenu vide"
    word_count = summary_data.get("word_count", 0)
    
    content = f"""# Synthèse médicale - {patient_id}

## Document analysé
- **Nom du fichier**: {document['filename']}
- **Type**: {document.get('file_type', 'unknown')}
- **Anonymisé**: {'Oui' if document.get('is_anonymized') else 'Non'}
- **Nombre de mots**: {word_count}
- **Entités PII détectées**: {len(document.get('pii_entities', []))}

## Extrait du document
{content_preview}...

## Analyse
Ce document contient {word_count} mots et {'a été anonymisé' if document.get('is_anonymized') else "n'a pas été anonymisé"}.
{'Des informations personnelles identifiables ont été détectées et anonymisées.' if document.get('is_anonymized') else ''}

## État du traitement
- Date de création: {document.get('created_at', 'Inconnue')}
- Statut: Document réel du système
"""

    # Extract summary points from content (simplified - would use NLP in production)
    summary_points = [
        f"Document: {document['filename']}",
        f"Taille: {word_count} mots",
        f"Anonymisation: {'Effectuée' if document.get('is_anonymized') else 'Non effectuée'}",
    ]
    
    if document.get('pii_entities'):
        summary_points.append(f"{len(document['pii_entities'])} entité(s) PII détectée(s)")
    
    recommendations = [
        "Document analysé avec succès",
        "Contenu basé sur données réelles anonymisées" if document.get('is_anonymized') else "Attention: document non anonymisé",
    ]

    return {
        "title": f"Synthèse médicale - {document['filename']}",
        "content": content,
        "summary_points": summary_points,
        "recommendations": recommendations,
        "_metadata": {
            "used_anonymized_data": True,
            "documents_analyzed": 1,
            "word_count": word_count,
            "is_anonymized": document.get('is_anonymized', False),
            "pii_count": len(document.get('pii_entities', [])),
        }
    }

