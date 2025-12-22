"""
Document Classifier Model
Classifies medical documents into types
"""
import torch
import torch.nn as nn
from transformers import AutoTokenizer, AutoModel, AutoModelForSequenceClassification
from typing import Dict, List, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class DocumentClassifier:
    """
    Deep Learning model for medical document classification.
    Uses fine-tuned BERT (CamemBERT for French) for document type prediction.
    """
    
    DOCUMENT_TYPES = [
        "blood_test",          # Analyse de sang
        "xray",                # Radiographie
        "mri",                 # IRM
        "prescription",        # Ordonnance
        "medical_report",      # Compte-rendu médical
        "lab_result",          # Résultat de laboratoire
        "consultation_note"    # Note de consultation
    ]
    
    def __init__(
        self,
        model_path: Optional[str] = None,
        use_pretrained: bool = True,
        pretrained_model: str = "camembert-base",
        device: Optional[str] = None
    ):
        """
        Initialize Document Classifier
        
        Args:
            model_path: Path to fine-tuned model (if available)
            use_pretrained: Whether to use pre-trained model
            pretrained_model: Name of pre-trained model to use
            device: Device to run model on ('cpu' or 'cuda')
        """
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model_path = model_path
        self.use_pretrained = use_pretrained
        
        logger.info(f"Initializing DocumentClassifier on {self.device}")
        
        try:
            if model_path and Path(model_path).exists() and not use_pretrained:
                # Load fine-tuned model
                logger.info(f"Loading fine-tuned model from {model_path}")
                model_file = Path(model_path) / "model.pth"
                
                if model_file.exists():
                    # Load custom trained model (PyTorch format)
                    logger.info(f"Loading custom PyTorch model from {model_file}")
                    
                    # Load config to get base model
                    config_file = Path(model_path) / "config.json"
                    base_model = pretrained_model  # default
                    if config_file.exists():
                        import json
                        with open(config_file) as f:
                            config = json.load(f)
                        base_model = config.get("base_model", pretrained_model)
                        logger.info(f"Using base model from config: {base_model}")
                    
                    # Load tokenizer from model path (saved with model)
                    try:
                        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
                        logger.info("✓ Tokenizer loaded from model path")
                    except Exception as e:
                        logger.warning(f"Could not load tokenizer from {model_path}, using base model tokenizer: {e}")
                        self.tokenizer = AutoTokenizer.from_pretrained(base_model)
                    
                    # Build model architecture using base model
                    logger.info(f"Building model architecture with {base_model}...")
                    self.model = self._build_model(base_model)
                    
                    # Load trained weights
                    logger.info(f"Loading trained weights from {model_file}...")
                    checkpoint = torch.load(model_file, map_location=self.device)
                    
                    # Extract model state_dict if wrapped
                    if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
                        logger.info("✓ Found wrapped state_dict, extracting model weights")
                        state_dict = checkpoint["model_state_dict"]
                    else:
                        state_dict = checkpoint
                    
                    # Fix key names: camembert.* -> roberta.* 
                    # (HuggingFace CamemBERT internally uses RoBERTa architecture)
                    fixed_state_dict = {}
                    keys_mapped = 0
                    for key, value in state_dict.items():
                        if key.startswith('camembert.'):
                            new_key = key.replace('camembert.', 'roberta.')
                            fixed_state_dict[new_key] = value
                            keys_mapped += 1
                        else:
                            fixed_state_dict[key] = value
                    
                    if keys_mapped > 0:
                        logger.info(f"✓ Mapped {keys_mapped} camembert.* keys to roberta.*")
                    
                    # Load with strict=False to allow missing keys (like pooler)
                    missing_keys, unexpected_keys = self.model.load_state_dict(fixed_state_dict, strict=False)
                    
                    if missing_keys:
                        logger.info(f"Missing keys (usually OK): {len(missing_keys)} keys")
                    if unexpected_keys:
                        logger.warning(f"Unexpected keys: {unexpected_keys[:3]}")
                    
                    logger.info("✓ Loaded trained weights successfully")
                else:
                    # Try HuggingFace format
                    logger.info("model.pth not found, trying HuggingFace format...")
                    self.tokenizer = AutoTokenizer.from_pretrained(model_path)
                    self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
            else:
                # Load pre-trained model
                logger.info(f"Loading pre-trained model: {pretrained_model}")
                self.tokenizer = AutoTokenizer.from_pretrained(pretrained_model)
                self.model = self._build_model(pretrained_model)
            
            self.model.to(self.device)
            self.model.eval()
            logger.info("DocumentClassifier initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing DocumentClassifier: {e}")
            raise
    
    def _build_model(self, pretrained_model: str) -> nn.Module:
        """Build classification model with BERT backbone"""
        try:
            # Try to load as sequence classification model
            model = AutoModelForSequenceClassification.from_pretrained(
                pretrained_model,
                num_labels=len(self.DOCUMENT_TYPES),
                problem_type="single_label_classification"
            )
            return model
        except:
            # Build custom classification head
            bert = AutoModel.from_pretrained(pretrained_model)
            
            class BERTClassifier(nn.Module):
                def __init__(self, bert_model, num_classes):
                    super().__init__()
                    self.bert = bert_model
                    self.dropout = nn.Dropout(0.3)
                    self.classifier = nn.Linear(768, num_classes)
                
                def forward(self, input_ids, attention_mask):
                    outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
                    pooled_output = outputs.pooler_output
                    pooled_output = self.dropout(pooled_output)
                    logits = self.classifier(pooled_output)
                    return {"logits": logits}
            
            return BERTClassifier(bert, len(self.DOCUMENT_TYPES))
    
    @torch.no_grad()
    def predict(self, text: str, max_length: int = 512) -> Dict:
        """
        Predict document type with confidence scores.
        
        Args:
            text: Document text content
            max_length: Maximum sequence length
            
        Returns:
            Dict with predicted_class, confidence, and all probabilities
        """
        try:
            # Tokenize
            encoded = self.tokenizer(
                text,
                truncation=True,
                padding="max_length",
                max_length=max_length,
                return_tensors="pt"
            )
            
            input_ids = encoded["input_ids"].to(self.device)
            attention_mask = encoded["attention_mask"].to(self.device)
            
            # Predict
            outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
            
            # Handle different output formats
            if isinstance(outputs, dict):
                logits = outputs["logits"]
            else:
                logits = outputs.logits
            
            probabilities = torch.softmax(logits, dim=1)[0]
            
            predicted_idx = torch.argmax(probabilities).item()
            predicted_class = self.DOCUMENT_TYPES[predicted_idx]
            confidence = probabilities[predicted_idx].item()
            
            return {
                "predicted_class": predicted_class,
                "confidence": float(confidence),
                "all_probabilities": {
                    doc_type: float(prob)
                    for doc_type, prob in zip(self.DOCUMENT_TYPES, probabilities.cpu().numpy())
                },
                "model_used": "fine_tuned" if not self.use_pretrained else "pretrained"
            }
            
        except Exception as e:
            logger.error(f"Error in prediction: {e}")
            return {
                "predicted_class": "unknown",
                "confidence": 0.0,
                "error": str(e)
            }
    
    @torch.no_grad()
    def predict_batch(self, texts: List[str], max_length: int = 512) -> List[Dict]:
        """Batch prediction for multiple documents"""
        try:
            # Tokenize batch
            encoded = self.tokenizer(
                texts,
                truncation=True,
                padding=True,
                max_length=max_length,
                return_tensors="pt"
            )
            
            input_ids = encoded["input_ids"].to(self.device)
            attention_mask = encoded["attention_mask"].to(self.device)
            
            # Predict
            outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
            
            if isinstance(outputs, dict):
                logits = outputs["logits"]
            else:
                logits = outputs.logits
            
            probabilities = torch.softmax(logits, dim=1)
            
            results = []
            for i, probs in enumerate(probabilities):
                predicted_idx = torch.argmax(probs).item()
                results.append({
                    "predicted_class": self.DOCUMENT_TYPES[predicted_idx],
                    "confidence": float(probs[predicted_idx].item()),
                    "all_probabilities": {
                        doc_type: float(prob)
                        for doc_type, prob in zip(self.DOCUMENT_TYPES, probs.cpu().numpy())
                    }
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error in batch prediction: {e}")
            return [{"error": str(e)} for _ in texts]
    
    def get_model_info(self) -> Dict:
        """Get model information"""
        return {
            "model_type": "DocumentClassifier",
            "classes": self.DOCUMENT_TYPES,
            "num_classes": len(self.DOCUMENT_TYPES),
            "device": str(self.device),
            "model_path": str(self.model_path),
            "using_pretrained": self.use_pretrained
        }
