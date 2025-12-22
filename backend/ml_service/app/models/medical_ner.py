"""
Medical Named Entity Recognition Model
Extracts medical entities from text
"""
import torch
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
from typing import List, Dict, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class MedicalNER:
    """
    BioBERT-based Named Entity Recognition for medical text.
    Extracts: diseases, medications, symptoms, dosages, dates, etc.
    """
    
    ENTITY_LABELS = {
        "DISEASE": "Maladie / Disease",
        "MEDICATION": "Médicament / Medication",
        "SYMPTOM": "Symptôme / Symptom",
        "DOSAGE": "Dosage",
        "DATE": "Date",
        "PROCEDURE": "Procédure médicale",
        "ANATOMY": "Anatomie",
        "TEST": "Test / Analyse"
    }
    
    def __init__(
        self,
        model_path: Optional[str] = None,
        use_pretrained: bool = True,
        pretrained_model: str = "dmis-lab/biobert-v1.1",
        device: Optional[str] = None
    ):
        """
        Initialize Medical NER
        
        Args:
            model_path: Path to fine-tuned model
            use_pretrained: Whether to use pre-trained model
            pretrained_model: Name of pre-trained model
            device: Device to run on
        """
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model_path = model_path
        self.use_pretrained = use_pretrained
        
        logger.info(f"Initializing MedicalNER on {self.device}")
        logger.info(f"  model_path: {model_path}")
        logger.info(f"  use_pretrained: {use_pretrained}")
        logger.info(f"  pretrained_model: {pretrained_model}")
        
        try:
            if model_path and Path(model_path).exists() and not use_pretrained:
                # Load fine-tuned model
                logger.info(f"Loading fine-tuned NER model from {model_path}")
                self.tokenizer = AutoTokenizer.from_pretrained(model_path)
                self.model = AutoModelForTokenClassification.from_pretrained(model_path)
            else:
                # Load pre-trained model
                logger.info(f"Loading pre-trained NER model: {pretrained_model}")
                if model_path:
                    logger.info(f"  Reason: use_pretrained={use_pretrained}, path_exists={Path(model_path).exists() if model_path else False}")
                self.tokenizer = AutoTokenizer.from_pretrained(pretrained_model)
                self.model = AutoModelForTokenClassification.from_pretrained(pretrained_model)
            
            # Create NER pipeline
            self.ner_pipeline = pipeline(
                "ner",
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if self.device == "cuda" else -1,
                aggregation_strategy="simple",  # Combine sub-word tokens
                ignore_labels=[]  # Don't ignore any labels
            )
            
            logger.info("MedicalNER initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing MedicalNER: {e}")
            # Fallback to basic implementation
            self.ner_pipeline = None
            logger.warning("NER pipeline not available, using fallback")
    
    def extract_entities(self, text: str) -> List[Dict]:
        """
        Extract medical entities from text.
        
        Args:
            text: Medical text content
            
        Returns:
            List of entities with text, label, start, end, confidence
        """
        try:
            if self.ner_pipeline:
                # Use transformer model
                raw_entities = self.ner_pipeline(text)
                logger.info(f"NER pipeline returned {len(raw_entities)} raw entities")
                if len(raw_entities) > 0:
                    logger.info(f"First entity: {raw_entities[0]}")
                
                entities = []
                for ent in raw_entities:
                    entities.append({
                        "text": ent["word"],
                        "label": self._map_label(ent["entity_group"]),
                        "start": int(ent["start"]),
                        "end": int(ent["end"]),
                        "confidence": float(ent["score"])
                    })
                
                # Filter out low-quality entities (label 'O' means not an entity)
                valid_entities = [
                    e for e in entities 
                    if e["label"] != "O" and e["confidence"] > 0.3
                ]
                
                # Check if BioBERT results are poor quality
                avg_confidence = sum(e["confidence"] for e in valid_entities) / len(valid_entities) if valid_entities else 0
                has_mostly_O_labels = sum(1 for e in entities if e["label"] == "O") > len(entities) * 0.5
                
                # Use fallback if BioBERT returns poor results
                if len(valid_entities) == 0 or avg_confidence < 0.4 or has_mostly_O_labels:
                    logger.warning(f"BioBERT quality poor (valid={len(valid_entities)}, avg_conf={avg_confidence:.2f}, O_labels={has_mostly_O_labels}), using fallback")
                    entities = self._fallback_extraction(text)
                    logger.info(f"Fallback found {len(entities)} entities")
                else:
                    entities = valid_entities
                    logger.info(f"Using BioBERT results: {len(entities)} entities")
                
                return entities
            else:
                # Fallback: simple keyword matching
                return self._fallback_extraction(text)
                
        except Exception as e:
            logger.error(f"Error extracting entities: {e}")
            return []
    
    def _map_label(self, label: str) -> str:
        """Map model label to our standardized labels"""
        label_upper = label.upper()
        
        # Map common NER labels
        if any(x in label_upper for x in ["DISEASE", "DISORDER", "CONDITION"]):
            return "DISEASE"
        elif any(x in label_upper for x in ["MEDICATION", "DRUG", "MEDICINE"]):
            return "MEDICATION"
        elif any(x in label_upper for x in ["SYMPTOM", "SIGN"]):
            return "SYMPTOM"
        elif any(x in label_upper for x in ["DOSAGE", "DOSE"]):
            return "DOSAGE"
        elif any(x in label_upper for x in ["DATE", "TIME"]):
            return "DATE"
        elif any(x in label_upper for x in ["PROCEDURE", "TREATMENT"]):
            return "PROCEDURE"
        elif any(x in label_upper for x in ["ANATOMY", "BODY"]):
            return "ANATOMY"
        elif any(x in label_upper for x in ["TEST", "LAB", "ANALYSIS"]):
            return "TEST"
        else:
            return label
    
    def _fallback_extraction(self, text: str) -> List[Dict]:
        """Fallback: Comprehensive keyword-based entity extraction for French medical text"""
        import re
        entities = []
        
        # Comprehensive French medical keywords
        keywords = {
            "DISEASE": [
                "diabète", "hypertension", "cancer", "infection", "pneumonie", "grippe",
                "arthrose", "asthme", "bronchite", "hepatite", "cholestérol", "anémie",
                "migraine", "allergie", "eczéma", "psoriasis", "obésité", "dépression",
                "anxiété", "insomnie", "angine", "otite", "sinusite", "gastrite",
                "colite", "cystite", "thrombose", "embolie", "infarctus", "avc"
            ],
            "MEDICATION": [
                "paracétamol", "ibuprofène", "amoxicilline", "aspirine", "doliprane",
                "metformine", "ramipril", "atorvastatine", "oméprazole", "levothyrox",
                "ventoline", "cortisone", "insuline", "antibiotique", "antalgique",
                "anti-inflammatoire", "antihistaminique", "antidépresseur", "anxiolytique",
                "bêta-bloquant", "diurétique", "statine", "ipp", "ains"
            ],
            "SYMPTOM": [
                "douleur", "fièvre", "toux", "fatigue", "nausée", "vertige",
                "céphalée", "maux de tête", "vomissement", "diarrhée", "constipation",
                "essoufflement", "palpitation", "tremblements", "sueur", "frisson",
                "démangeaison", "éruption", "rougeur", "gonflement", "œdème",
                "crampe", "spasme", "picotement", "engourdissement", "malaise"
            ],
            "TEST": [
                "analyse", "scanner", "irm", "radiographie", "échographie", "bilan",
                "prise de sang", "électrocardiogramme", "ecg", "eeg", "endoscopie",
                "coloscopie", "mammographie", "densitométrie", "scintigraphie",
                "pet scan", "doppler", "fibroscopie", "biopsie", "ponction"
            ],
            "PROCEDURE": [
                "intervention", "opération", "chirurgie", "hospitalisation",
                "consultation", "examen", "traitement", "suivi", "rééducation",
                "kinésithérapie", "vaccination", "perfusion", "injection", "pansement"
            ],
            "ANATOMY": [
                "cœur", "poumon", "foie", "rein", "estomac", "intestin",
                "cerveau", "artère", "veine", "muscle", "os", "articulation",
                "peau", "nerf", "pancréas", "rate", "thyroïde", "prostate"
            ]
        }
        
        text_lower = text.lower()
        processed_ranges = []  # Track already extracted positions to avoid duplicates
        
        for label, words in keywords.items():
            for word in words:
                # Use regex to find whole word matches
                pattern = r'\b' + re.escape(word) + r'\b'
                for match in re.finditer(pattern, text_lower):
                    start, end = match.span()
                    
                    # Check if this range overlaps with already extracted entity
                    overlaps = any(
                        (start >= existing_start and start < existing_end) or
                        (end > existing_start and end <= existing_end)
                        for existing_start, existing_end in processed_ranges
                    )
                    
                    if not overlaps:
                        entities.append({
                            "text": text[start:end],
                            "label": label,
                            "start": start,
                            "end": end,
                            "confidence": 0.75  # Lower confidence for keyword-based
                        })
                        processed_ranges.append((start, end))
        
        # Sort by position in text
        entities.sort(key=lambda x: x["start"])
        
        return entities
    
    def annotate_text(self, text: str) -> Dict:
        """Return text with entity annotations"""
        entities = self.extract_entities(text)
        
        return {
            "text": text,
            "entities": entities,
            "entity_count": len(entities),
            "entity_types": list(set(e["label"] for e in entities))
        }
    
    def get_model_info(self) -> Dict:
        """Get model information"""
        return {
            "model_type": "MedicalNER",
            "entity_labels": self.ENTITY_LABELS,
            "device": str(self.device),
            "model_path": str(self.model_path),
            "using_pretrained": self.use_pretrained,
            "pipeline_available": self.ner_pipeline is not None
        }
