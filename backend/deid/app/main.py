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
            
            # ========================================================================
            # LISTE COMPLÈTE DES FAUX POSITIFS - TERMES MÉDICAUX À PRÉSERVER
            # Basée sur les standards HIPAA Safe Harbor Method
            # ========================================================================
            # Ce qui DOIT être détecté comme PII (18 identifiants HIPAA):
            # 1. Noms de personnes réelles
            # 2. Adresses géographiques (rue, ville, code postal)
            # 3. Dates précises (sauf année) liées au patient
            # 4. Numéros de téléphone
            # 5. Numéros de fax
            # 6. Adresses email
            # 7. Numéros de sécurité sociale
            # 8. Numéros de dossier médical
            # 9. Numéros d'assurance santé
            # 10. Numéros de compte
            # 11. Numéros de certificat/licence
            # 12. Identifiants de véhicule (plaques)
            # 13. Identifiants d'appareil médical (séries)
            # 14. URLs web
            # 15. Adresses IP
            # 16. Identifiants biométriques
            # 17. Photos de visage
            # 18. Autres identifiants uniques
            #
            # Ce qui NE DOIT PAS être détecté (terminologie médicale):
            false_positive_patterns = [
                # ===== 1. ÉTIQUETTES DE CHAMPS ET STRUCTURE DE DOCUMENT =====
                "numero", "numéro", "nom", "prenom", "prénom", "adresse", 
                "telephone", "téléphone", "tel", "email", "mail", "courriel",
                "date", "sexe", "âge", "age", "genre",
                "motif", "objet", "sujet",
                "antecedents", "antécédents", "historique", "histoire",
                "prochain", "suivant", "précédent", "precedent",
                "rdv", "rendez-vous", "consultation",
                "naissance", "admission", "sortie", "hospitalisation",
                "référence", "reference", "dossier", "fichier",
                "prescrit", "prescrite", "prescription", "prescripteur",
                "note", "notes", "remarque", "remarques", "observation", "observations",
                "signature", "signé", "signe", "paraphe",
                "recommandations", "recommandation", "conseils", "conseil",
                "mesures", "mesure", "hygiéno-diététiques", "hygieno-dietetiques",
                "hygiéno-diététique", "hygieno-dietetique", "hygiène", "hygiene", "diététique", "dietetique",
                
                # ===== 2. TERMES DE GENRE ET ÉTAT CIVIL =====
                "masculin", "féminin", "feminin", "homme", "femme",
                "male", "female", "garçon", "garcon", "fille",
                "monsieur", "madame", "mademoiselle", "mr", "mme", "mlle",
                
                # ===== 3. SIGNES VITAUX ET MESURES =====
                "température", "temperature", "temp", "fièvre", "fievre",
                "pression", "tension", "artérielle", "arterielle", "systolique", "diastolique",
                "fréquence", "frequence", "cardiaque", "rythme", "pouls",
                "poids", "taille", "imc", "indice", "masse", "corporelle",
                "saturation", "spo2", "oxygène", "oxygene",
                "glycémie", "glycemie", "glucose", "hba1c",
                
                # ===== 4. PERSONNEL MÉDICAL (termes généraux, pas noms propres) =====
                "patient", "patiente", "malade",
                "medecin", "médecin", "docteur", "dr", "professeur", "pr",
                "infirmier", "infirmière", "infirmiere", "ide",
                "chirurgien", "anesthésiste", "anesthesiste",
                "cardiologue", "dermatologue", "radiologue", "neurologue",
                "pédiatre", "pediatre", "gériatre", "geriatre",
                "pharmacien", "sage-femme", "kinésithérapeute", "kinesitherapeute",
                
                # ===== 5. TERMES MÉDICAUX GÉNÉRAUX =====
                "diagnostic", "diagnostique", "pronostic",
                "traitement", "thérapie", "therapie", "cure", "soin", "soins",
                "prescription", "ordonnance", "posologie",
                "consultation", "examen", "bilan", "check-up",
                "analyse", "test", "screening", "dépistage", "depistage",
                "resultats", "résultats", "rapport", "compte-rendu", "compte", "rendu",
                "symptomes", "symptômes", "signes", "manifestation",
                "clinique", "medical", "médical", "thérapeutique", "therapeutique",
                "pathologie", "maladie", "affection", "trouble",
                "syndrome", "epidemie", "épidémie", "contagieux", "contagieuse",
                "régime", "regime", "alimentaire", "nutrition", "nutritionnel", "nutritionnelle",
                "pauvre", "riche", "équilibré", "equilibre", "équilibre",
                "sel", "sucre", "graisses", "graisse", "saturées", "saturees", "saturée", "saturee",
                "lipides", "lipide", "glucides", "glucide", "protéines", "proteine",
                "activité", "activite", "physique", "exercice", "sport",
                "marche", "course", "natation", "gymnastique",
                "arrêt", "arret", "cessation", "abstinence", "sevrage",
                "tabac", "cigarette", "alcool", "drogue", "cannabis",
                "contrôle", "controle", "surveillance", "monitoring", "suivi",
                
                # ===== 6. MALADIES CARDIOVASCULAIRES =====
                "hypertension", "hta", "hypotension",
                "infarctus", "cardiopathie", "angine", "angor",
                "arythmie", "fibrillation", "tachycardie", "bradycardie",
                "insuffisance", "cardiaque", "coronarien", "coronarienne",
                "avc", "accident", "vasculaire", "cérébral", "cerebral",
                "thrombose", "embolie", "phlébite", "phlebite",
                "artériosclérose", "arteriosclerose", "athérosclérose", "atherosclerose",
                
                # ===== 7. MALADIES MÉTABOLIQUES ET ENDOCRINIENNES =====
                "diabete", "diabète", "glycémie", "glycemie",
                "cholesterol", "cholestérol", "triglycérides", "triglycerides",
                "hyperlipidémie", "hyperlipidemie", "dyslipidémie", "dyslipidemie",
                "hypothyroïdie", "hypothyroidie", "hyperthyroïdie", "hyperthyroidie",
                "thyroïde", "thyroide", "thyroïdien", "thyroidien",
                "obésité", "obesite", "surpoids", "maigreur",
                
                # ===== 8. MALADIES INFECTIEUSES =====
                "infection", "infectieux", "infectieuse",
                "inflammation", "inflammatoire",
                "cystite", "pyélonéphrite", "pyelonephrite", "néphrite", "nephrite",
                "angine", "pharyngite", "amygdalite",
                "grippe", "influenza", "rhume", "rhinopharyngite",
                "bronchite", "pneumonie", "tuberculose",
                "gastro-entérite", "gastro", "gastroenterite",
                "covid", "coronavirus", "sars", "vih", "sida",
                "hépatite", "hepatite", "cirrhose",
                "septicémie", "septicemie", "sepsis",
                
                # ===== 9. MALADIES RESPIRATOIRES =====
                "asthme", "asthmatique", "bronchite", "bpco",
                "pneumonie", "pleurésie", "pleuresie",
                "dyspnée", "dyspnee", "essoufflement",
                "apnée", "apnee", "ronflement",
                "emphysème", "emphyseme", "fibrose",
                
                # ===== 10. MALADIES OSTÉO-ARTICULAIRES =====
                "arthrose", "arthrite", "rhumatisme",
                "polyarthrite", "spondylarthrite",
                "ostéoporose", "osteoporose",
                "fracture", "luxation", "entorse", "foulure",
                "tendinite", "bursite", "épicondylite", "epicondylite",
                "lombalgie", "sciatique", "hernie", "discale",
                "cervicalgie", "dorsalgie",
                
                # ===== 11. MALADIES NEUROLOGIQUES =====
                "migraine", "céphalée", "cephalee", "mal", "tête", "tete",
                "épilepsie", "epilepsie", "convulsion", "crise",
                "parkinson", "alzheimer", "démence", "demence",
                "sclérose", "sclerose", "myasthénie", "myasthenie",
                "neuropathie", "névralgie", "nevralgie",
                "vertige", "étourdissement", "etourdissement",
                
                # ===== 12. MALADIES DIGESTIVES =====
                "gastrite", "ulcère", "ulcere",
                "reflux", "rgo", "brûlure", "brulure", "estomac",
                "colite", "maladie", "crohn", "rectocolite",
                "diverticulite", "constipation", "diarrhée", "diarrhee",
                "hémorroïdes", "hemorroides", "fissure", "anale",
                
                # ===== 13. CANCERS ET TUMEURS =====
                "cancer", "cancéreux", "cancereuse",
                "tumeur", "néoplasie", "neoplasie",
                "carcinome", "sarcome", "mélanome", "melanome",
                "leucémie", "leucemie", "lymphome",
                "métastase", "metastase", "métastatique", "metastatique",
                "chimiothérapie", "chimiotherapie", "radiothérapie", "radiotherapie",
                "oncologie", "oncologique",
                
                # ===== 14. ALLERGIES ET IMMUNOLOGIE =====
                "allergie", "allergique", "atopie",
                "urticaire", "eczéma", "eczema", "dermatite",
                "anaphylaxie", "choc", "allergique",
                "immunité", "immunite", "immunologique",
                "auto-immune", "auto", "immune",
                
                # ===== 15. PARTIES DU CORPS ET ANATOMIE =====
                # Tête et cou
                "tête", "tete", "crâne", "crane", "cerveau",
                "œil", "oeil", "yeux", "cornée", "cornee", "rétine", "retine",
                "oreille", "tympan", "audition",
                "nez", "sinus", "nasale", "odorat",
                "bouche", "langue", "dent", "gencive", "lèvre", "levre",
                "gorge", "pharynx", "larynx", "trachée", "trachee",
                "cou", "thyroïde", "thyroide",
                
                # Thorax
                "coeur", "cœur", "cardiaque", "coronaire",
                "poumon", "bronche", "alvéole", "alveole", "pleural",
                "thorax", "thoracique", "sein", "mammaire",
                
                # Abdomen
                "estomac", "gastrique",
                "foie", "hépatique", "hepatique", "biliaire",
                "pancréas", "pancreas", "pancréatique", "pancreatique",
                "rate", "splénique", "splenique",
                "intestin", "côlon", "colon", "rectum", "anus",
                "vésicule", "vesicule",
                
                # Système urinaire
                "rein", "rénal", "renal", "néphrétique", "nephretique",
                "vessie", "urètre", "uretre", "urinaire",
                "prostate", "prostatique",
                
                # Système reproducteur
                "utérus", "uterus", "utérin", "uterin",
                "ovaire", "ovarien", "ovarienne",
                "vagin", "vaginal", "vaginale",
                "testicule", "testiculaire",
                
                # Membres et squelette
                "bras", "avant-bras", "coude", "poignet", "main", "doigt",
                "jambe", "cuisse", "genou", "cheville", "pied", "orteil",
                "os", "osseux", "squelette", "vertèbre", "vertebre",
                "colonne", "vertébrale", "vertebrale", "lombaire",
                "articulation", "articulaire",
                
                # Peau
                "peau", "cutané", "cutane", "derme", "épiderme", "epiderme",
                
                # Vaisseaux
                "artère", "artere", "artériel", "arteriel",
                "veine", "veineux", "veineuse",
                "capillaire", "vasculaire",
                
                # ===== 16. TYPES ET QUALIFICATIFS MÉDICAUX =====
                "chirurgical", "chirurgicale", "opératoire", "operatoire",
                "aigu", "aiguë", "aigu", "aigue",
                "chronique", "récurrent", "recurrent", "récidivant", "recidivant",
                "complique", "compliqué", "compliquee", "compliquée",
                "bénin", "benin", "bénigne", "benigne",
                "malin", "maligne", "grave", "sévère", "severe",
                "léger", "leger", "légère", "legere", "modéré", "modere",
                "asymptomatique", "symptomatique",
                "primaire", "secondaire", "tertiaire",
                "bilatéral", "bilateral", "unilatéral", "unilateral",
                "proximal", "distal", "latéral", "lateral", "médian", "median",
                
                # ===== 17. BACTÉRIES, VIRUS ET MICROBES =====
                "bacterie", "bactérie", "bactérien", "bacterien",
                "virus", "viral", "virale",
                "champignon", "fongique", "mycose",
                "parasite", "parasitaire",
                "escherichia", "coli", "e. coli", "e.coli",
                "staphylocoque", "staphylococcus", "aureus",
                "streptocoque", "streptococcus",
                "salmonelle", "salmonella",
                "candida", "albicans",
                
                # ===== 18. ANALYSES ET RÉSULTATS DE LABORATOIRE =====
                "ecbu", "culot", "urinaire",
                "leucocytes", "hématies", "hematies", "globules",
                "nitrites", "protéinurie", "proteinurie",
                "crp", "protéine", "proteine", "réactive", "reactive",
                "créatinine", "creatinine", "urée", "uree",
                "transaminases", "bilirubine",
                "hémoglobine", "hemoglobine", "hématocrite", "hematocrite",
                "plaquettes", "coagulation", "inr",
                "tsh", "t3", "t4", "hormone",
                "elevee", "élevée", "elevé", "élevé",
                "diminue", "diminué", "diminuee", "diminuée",
                "normal", "normale", "anormal", "anormale",
                "positif", "positive", "négatif", "negatif", "négative", "negative",
                "isole", "isolé", "isolee", "isolée", "détecté", "detecte",
                
                # ===== 19. MÉDICAMENTS (liste exhaustive des plus courants) =====
                # Antibiotiques
                "antibiotique", "amoxicilline", "augmentin",
                "ciprofloxacine", "cipro", "ofloxacine",
                "azithromycine", "zithromax", "clarithromycine",
                "doxycycline", "métronidazole", "metronidazole",
                "céphalosporine", "cephalosporine", "ceftriaxone",
                
                # Antalgiques et anti-inflammatoires
                "paracetamol", "paracétamol", "doliprane", "efferalgan", "dafalgan",
                "ibuprofene", "ibuprofène", "advil", "nurofen",
                "aspirine", "kardegic",
                "codéine", "codeine", "tramadol", "morphine",
                "naproxène", "naproxene", "kétoprofène", "ketoprofene",
                
                # Cardiovasculaires
                "ramipril", "enalapril", "périndopril", "perindopril",
                "amlodipine", "nifédipine", "nifedipine",
                "bisoprolol", "métoprolol", "metoprolol", "aténolol", "atenolol",
                "atorvastatine", "simvastatine", "rosuvastatine",
                "clopidogrel", "plavix", "warfarine", "coumadine",
                
                # Diabète
                "metformine", "métformine", "glucophage",
                "insuline", "lantus", "novorapid",
                "gliclazide", "diamicron",
                
                # Autres classes
                "levothyrox", "l-thyroxine",
                "ventoline", "salbutamol", "bronchodilatateur", "bronchodilatateur",
                "cortisone", "prednisone", "prednisolone", "corticoïde", "corticoide",
                "omeprazole", "oméprazole", "esoméprazole", "esomeprazole",
                "lisinopril", "losartan", "valsartan",
                "furosémide", "furosemide", "lasilix",
                "spironolactone", "aldactone",
                
                # ===== 20. PROCÉDURES ET EXAMENS MÉDICAUX =====
                "scanner", "tdm", "tomodensitométrie", "tomodensitometrie",
                "irm", "résonance", "resonance", "magnétique", "magnetique",
                "radiographie", "radio", "rayon",
                "échographie", "echographie", "écho", "echo", "doppler",
                "endoscopie", "coloscopie", "gastroscopie",
                "biopsie", "ponction", "prélèvement", "prelevement",
                "ecg", "électrocardiogramme", "electrocardiogramme",
                "eeg", "électroencéphalogramme", "electroencephalogramme",
                "spirométrie", "spirometrie",
                "cathétérisme", "catheterisme",
                
                # ===== 21. TERMES ADMINISTRATIFS ET ORGANISATIONNELS =====
                "dossier", "fichier", "document", "formulaire",
                "hopital", "hôpital", "clinique", "dispensaire",
                "service", "département", "departement", "unité", "unite",
                "urgence", "urgences", "réanimation", "reanimation",
                "hospitalisation", "séjour", "sejour",
                "ambulatoire", "externe", "interne",
                "suivi", "contrôle", "controle", "surveillance",
                "cabinet", "centre", "établissement", "etablissement",
                "mutuelle", "assurance", "sécurité", "securite", "sociale",
                
                # ===== 22. TERMES TEMPORELS (contexte médical, pas dates exactes) =====
                "jour", "jours", "semaine", "semaines", "mois", "année", "annee", "années", "annees",
                "quotidien", "quotidienne", "journalier", "journalière", "journaliere",
                "hebdomadaire", "mensuel", "mensuelle", "annuel", "annuelle",
                "durée", "duree", "période", "periode", "délai", "delai",
                "minute", "minutes", "heure", "heures",
                "matin", "midi", "soir", "nuit", "après-midi", "apres-midi",
                "continu", "continue", "régulier", "regulier", "régulière", "reguliere",
                "dans", "depuis", "pendant", "durant",
                "par", "fois", "par jour", "par semaine",
                
                # ===== 23. VACCINS =====
                "vaccin", "vaccination", "immunisation",
                "bcg", "dtpolio", "ror", "rougeole", "oreillons", "rubéole", "rubeole",
                "hépatite", "hepatite", "pneumocoque", "méningocoque", "meningocoque",
                "grippe", "covid", "papillomavirus", "hpv",
                
                # ===== 24. TERMES DE QUANTITÉ ET FRÉQUENCE =====
                "dose", "dosage", "posologie",
                "fois", "prise", "comprimé", "comprime", "gélule", "gelule",
                "goutte", "gouttes", "cuillère", "cuillere", "sachet",
                "matin", "midi", "soir", "nuit", "coucher",
                "repas", "jeun", "jeûn", "avant", "après", "apres",
                "mg", "gramme", "grammes", "litre", "litres", "ml",
                
                # ===== 25. DISPOSITIFS MÉDICAUX =====
                "appareil", "dispositif", "matériel", "materiel",
                "prothèse", "prothese", "implant", "pace-maker", "pacemaker",
                "cathéter", "catheter", "sonde", "drain",
                "attelle", "plâtre", "platre", "bandage", "pansement",
                "perfusion", "seringue", "aiguille",
                
                # ===== 26. MOTS DE LIAISON ET PRÉPOSITIONS COURANTES =====
                "le", "la", "les", "un", "une", "des",
                "de", "du", "à", "au", "aux", "en", "et",
                "pour", "avec", "sans", "selon",
                "associée", "associe", "associé", "associees", "associés",
                "fictive", "fictif", "éducatif", "educatif", "éducative", "educative",
                "but", "objectif", "fin", "finalité", "finalite",
            ]
            
            filtered_results = []
            for result in analyzer_results:
                entity_text = request.content[result.start:result.end].strip()
                entity_text_lower = entity_text.lower()
                
                # ÉTAPE 1: Filtrage par correspondance exacte
                if entity_text_lower in false_positive_patterns:
                    logger.info(f"Filtré (exact): {entity_text} (type: {result.entity_type})")
                    continue
                
                # ÉTAPE 2: Ignorer les noms de médecins (doivent être anonymisés)
                is_doctor_name = any(title in entity_text for title in ["Dr.", "Dr ", "Docteur", "Pr.", "Professeur"])
                
                # ÉTAPE 3: Filtrage par correspondance partielle (termes composés)
                # Ne s'applique PAS aux noms de médecins
                is_medical_term = False
                if not is_doctor_name:
                    for medical_term in false_positive_patterns:
                        # Seulement pour les termes > 4 caractères pour éviter faux positifs
                        if len(medical_term) > 4 and medical_term in entity_text_lower:
                            logger.info(f"Filtré (partiel): {entity_text} (contient '{medical_term}', type: {result.entity_type})")
                            is_medical_term = True
                            break
                
                if is_medical_term:
                    continue
                
                # ÉTAPE 4: Filtrer les entités très courtes avec faible confiance
                if len(entity_text) < 3 and result.score < 0.9:
                    logger.info(f"Filtré (trop court): {entity_text} (confiance: {result.score})")
                    continue
                
                # ÉTAPE 5: Filtrer les mesures numériques (20 mg, 5 g, etc.)
                import re
                if re.match(r'^\d+[\s]*(mg|g|kg|ml|l|°c|mmhg|bpm|%|mm|cm|m)', entity_text_lower):
                    logger.info(f"Filtré (mesure): {entity_text}")
                    continue
                
                # ÉTAPE 6: Filtrer les termes qui commencent par des mots courants
                common_prefixes = ["traitement", "prescription", "mesures", "recommandations", "note", "régime", "regime", "activité", "activite"]
                starts_with_common = any(entity_text_lower.startswith(prefix) for prefix in common_prefixes)
                if starts_with_common and not is_doctor_name:
                    logger.info(f"Filtré (préfixe commun): {entity_text}")
                    continue
                
                # ÉTAPE 7: Filtrer les phrases composées uniquement de mots de liaison/termes médicaux
                # Exemple: "sel et en" = 3 mots dont tous sont dans notre liste
                words_in_entity = entity_text_lower.split()
                if len(words_in_entity) >= 2:  # Si l'entité contient plusieurs mots
                    words_matched = sum(1 for word in words_in_entity if word in false_positive_patterns)
                    if words_matched >= len(words_in_entity) - 1:  # Si presque tous les mots sont dans la liste
                        logger.info(f"Filtré (phrase composée de termes médicaux): {entity_text}")
                        continue
                    
                # Si toutes les vérifications passent, c'est probablement un vrai PII
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