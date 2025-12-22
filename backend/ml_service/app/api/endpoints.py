"""
ML Service API Endpoints
"""
from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


# Request/Response Models
class TextInput(BaseModel):
    """Input model for text processing"""
    text: str = Field(..., description="Text content to process")


class ClassificationResponse(BaseModel):
    """Response model for document classification"""
    predicted_class: str
    confidence: float
    all_probabilities: Dict[str, float]
    model_used: Optional[str] = None


class Entity(BaseModel):
    """Entity model"""
    text: str
    label: str
    start: int
    end: int
    confidence: float


class NERResponse(BaseModel):
    """Response model for NER"""
    entities: List[Entity]
    entity_count: int
    entity_types: List[str]


class DocumentAnalysisResponse(BaseModel):
    """Complete document analysis response"""
    text: str
    classification: Optional[ClassificationResponse] = None
    entities: Optional[List[Entity]] = None
    entity_count: int = 0
    entity_types: Optional[List[str]] = None
    processing_status: str
    processing_time_ms: int = 0


# Dependency to get model manager
def get_model_manager(request: Request):
    """Get model manager from app state"""
    return request.app.state.model_manager


@router.post("/classify", response_model=ClassificationResponse)
async def classify_document(
    input_data: TextInput,
    model_manager=Depends(get_model_manager)
):
    """
    Classify medical document type
    
    - **text**: Document text content in French
    
    Returns document type classification with confidence scores.
    """
    try:
        result = model_manager.classify_document(input_data.text)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
        
    except Exception as e:
        logger.error(f"Classification endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/extract-entities", response_model=List[Entity])
async def extract_entities(
    input_data: TextInput,
    model_manager=Depends(get_model_manager)
):
    """
    Extract medical entities from text
    
    - **text**: Medical text content
    
    Returns list of extracted entities (diseases, medications, symptoms, etc.)
    """
    try:
        entities = model_manager.extract_entities(input_data.text)
        return entities
        
    except Exception as e:
        logger.error(f"Entity extraction endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/annotate", response_model=NERResponse)
async def annotate_text(
    input_data: TextInput,
    model_manager=Depends(get_model_manager)
):
    """
    Annotate text with medical entities
    
    - **text**: Text to annotate
    
    Returns annotated text with entity information.
    """
    try:
        result = model_manager.annotate_text(input_data.text)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "entities": result.get("entities", []),
            "entity_count": result.get("entity_count", 0),
            "entity_types": result.get("entity_types", [])
        }
        
    except Exception as e:
        logger.error(f"Annotation endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze", response_model=DocumentAnalysisResponse)
async def analyze_document(
    input_data: TextInput,
    model_manager=Depends(get_model_manager)
):
    """
    Complete document analysis pipeline
    
    - **text**: Document text content
    
    Performs both classification and entity extraction in one call.
    This is the recommended endpoint for full document processing.
    """
    try:
        result = model_manager.process_document(input_data.text)
        return result
        
    except Exception as e:
        logger.error(f"Analysis endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models/info")
async def get_models_info(model_manager=Depends(get_model_manager)):
    """
    Get information about loaded models
    
    Returns details about available models, their status, and configuration.
    """
    try:
        return model_manager.get_models_info()
        
    except Exception as e:
        logger.error(f"Models info endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models/types")
async def get_document_types():
    """
    Get list of supported document types
    
    Returns list of document types that the classifier can identify.
    """
    from app.models.document_classifier import DocumentClassifier
    
    return {
        "document_types": DocumentClassifier.DOCUMENT_TYPES,
        "count": len(DocumentClassifier.DOCUMENT_TYPES)
    }


@router.get("/models/entity-labels")
async def get_entity_labels():
    """
    Get list of supported entity labels
    
    Returns list of medical entity types that can be extracted.
    """
    from app.models.medical_ner import MedicalNER
    
    return {
        "entity_labels": MedicalNER.ENTITY_LABELS,
        "count": len(MedicalNER.ENTITY_LABELS)
    }
