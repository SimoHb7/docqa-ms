"""
Model Manager Service
Manages loading and inference of all ML models
"""
import logging
from typing import Dict, List, Optional
from app.models.document_classifier import DocumentClassifier
from app.models.medical_ner import MedicalNER

logger = logging.getLogger(__name__)


class ModelManager:
    """
    Manages all ML models for the service.
    Handles model loading, caching, and inference routing.
    """
    
    def __init__(
        self,
        classifier_path: Optional[str] = None,
        classifier_pretrained: str = "camembert-base",
        classifier_use_pretrained: bool = True,
        ner_path: Optional[str] = None,
        ner_pretrained: str = "dmis-lab/biobert-v1.1",
        ner_use_pretrained: bool = True,
        device: str = "cpu"
    ):
        """
        Initialize Model Manager
        
        Args:
            classifier_path: Path to fine-tuned classifier
            classifier_pretrained: Pre-trained classifier name
            classifier_use_pretrained: Use pre-trained or fine-tuned
            ner_path: Path to fine-tuned NER model
            ner_pretrained: Pre-trained NER name
            ner_use_pretrained: Use pre-trained or fine-tuned
            device: Device to run models on
        """
        self.device = device
        self.models = {}
        
        logger.info("Initializing ModelManager...")
        
        # Load Document Classifier
        try:
            logger.info("Loading Document Classifier...")
            self.models["classifier"] = DocumentClassifier(
                model_path=classifier_path,
                use_pretrained=classifier_use_pretrained,
                pretrained_model=classifier_pretrained,
                device=device
            )
            logger.info("✓ Document Classifier loaded")
        except Exception as e:
            logger.error(f"Failed to load Document Classifier: {e}")
            self.models["classifier"] = None
        
        # Load Medical NER
        try:
            logger.info("Loading Medical NER...")
            self.models["ner"] = MedicalNER(
                model_path=ner_path,
                use_pretrained=ner_use_pretrained,
                pretrained_model=ner_pretrained,
                device=device
            )
            logger.info("✓ Medical NER loaded")
        except Exception as e:
            logger.error(f"Failed to load Medical NER: {e}")
            self.models["ner"] = None
        
        logger.info("ModelManager initialized successfully")
    
    def classify_document(self, text: str) -> Dict:
        """
        Classify document type
        
        Args:
            text: Document text content
            
        Returns:
            Classification result
        """
        if not self.models.get("classifier"):
            return {"error": "Classifier model not available"}
        
        try:
            return self.models["classifier"].predict(text)
        except Exception as e:
            logger.error(f"Classification error: {e}")
            return {"error": str(e)}
    
    def extract_entities(self, text: str) -> List[Dict]:
        """
        Extract medical entities from text
        
        Args:
            text: Medical text content
            
        Returns:
            List of entities
        """
        if not self.models.get("ner"):
            return []
        
        try:
            return self.models["ner"].extract_entities(text)
        except Exception as e:
            logger.error(f"Entity extraction error: {e}")
            return []
    
    def annotate_text(self, text: str) -> Dict:
        """
        Annotate text with entities
        
        Args:
            text: Text to annotate
            
        Returns:
            Annotated text with entities
        """
        if not self.models.get("ner"):
            return {"error": "NER model not available"}
        
        try:
            return self.models["ner"].annotate_text(text)
        except Exception as e:
            logger.error(f"Annotation error: {e}")
            return {"error": str(e)}
    
    def process_document(self, text: str) -> Dict:
        """
        Full document processing pipeline
        
        Args:
            text: Document text
            
        Returns:
            Complete analysis including classification and entities
        """
        import time
        start_time = time.time()
        
        result = {
            "text": text,
            "classification": None,
            "entities": None,
            "entity_count": 0,
            "processing_status": "success",
            "processing_time_ms": 0
        }
        
        try:
            # Classify document
            if self.models.get("classifier"):
                result["classification"] = self.classify_document(text)
            
            # Extract entities
            if self.models.get("ner"):
                entities = self.extract_entities(text)
                result["entities"] = entities
                result["entity_count"] = len(entities)
                result["entity_types"] = list(set(e["label"] for e in entities))
            
            # Calculate processing time
            result["processing_time_ms"] = int((time.time() - start_time) * 1000)
            
        except Exception as e:
            logger.error(f"Document processing error: {e}")
            result["processing_status"] = "error"
            result["error"] = str(e)
            result["processing_time_ms"] = int((time.time() - start_time) * 1000)
        
        return result
    
    def get_models_info(self) -> Dict:
        """Get information about loaded models"""
        info = {
            "loaded_models": list(self.models.keys()),
            "device": self.device,
            "models": {}
        }
        
        for name, model in self.models.items():
            if model:
                try:
                    info["models"][name] = model.get_model_info()
                except:
                    info["models"][name] = {"status": "loaded"}
            else:
                info["models"][name] = {"status": "not_available"}
        
        return info
    
    def reload_model(self, model_name: str):
        """Reload a specific model"""
        logger.info(f"Reloading model: {model_name}")
        # Implementation for model reloading
        # Useful when fine-tuned model is uploaded
        pass
