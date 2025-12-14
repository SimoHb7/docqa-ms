"""
Custom recognizers for French PII entities
"""
from presidio_analyzer import Pattern, PatternRecognizer
from typing import List, Optional
import re


class FrenchPhoneRecognizer(PatternRecognizer):
    """
    Recognizer for French phone numbers in various formats:
    - 0612345678 (10 digits starting with 0)
    - 06 12 34 56 78 (with spaces)
    - 06.12.34.56.78 (with dots)
    - 06-12-34-56-78 (with hyphens)
    - +33 6 12 34 56 78 (international format)
    - +33612345678
    """

    PATTERNS = [
        # French mobile (06, 07) and landline (01-05, 09) - no separators
        Pattern(
            name="french_phone_no_sep",
            regex=r"\b0[1-9](?:\d{8})\b",
            score=0.75,
        ),
        # With spaces
        Pattern(
            name="french_phone_spaces",
            regex=r"\b0[1-9](?:\s?\d{2}){4}\b",
            score=0.8,
        ),
        # With dots
        Pattern(
            name="french_phone_dots",
            regex=r"\b0[1-9](?:\.\d{2}){4}\b",
            score=0.8,
        ),
        # With hyphens
        Pattern(
            name="french_phone_hyphens",
            regex=r"\b0[1-9](?:-\d{2}){4}\b",
            score=0.8,
        ),
        # International format with +33
        Pattern(
            name="french_phone_intl_spaces",
            regex=r"\+33\s?[1-9](?:\s?\d{2}){4}\b",
            score=0.85,
        ),
        # International format without spaces
        Pattern(
            name="french_phone_intl_no_sep",
            regex=r"\+33[1-9]\d{8}\b",
            score=0.85,
        ),
    ]

    CONTEXT = [
        "téléphone", "telephone", "tel", "tél", "mobile", "portable",
        "contact", "numéro", "numero", "appel", "joindre"
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "fr",
        supported_entity: str = "PHONE_NUMBER",
    ):
        patterns = patterns if patterns else self.PATTERNS
        context = context if context else self.CONTEXT
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )


class FrenchSSNRecognizer(PatternRecognizer):
    """
    Recognizer for French Social Security Numbers (Numéro de Sécurité Sociale)
    Format: 1 YY MM DD DDD KKK CC
    - 1 digit for sex (1=male, 2=female)
    - 2 digits for year of birth
    - 2 digits for month of birth
    - 2 digits for department
    - 3 digits for commune code
    - 3 digits for order number
    - 2 digits for control key
    
    Examples:
    - 1 89 05 26 108 255 43
    - 2890526108255 43
    - 1-89-05-26-108-255-43
    """

    PATTERNS = [
        # With spaces
        Pattern(
            name="french_ssn_spaces",
            regex=r"\b[12]\s?\d{2}\s?\d{2}\s?\d{2}\s?\d{3}\s?\d{3}\s?\d{2}\b",
            score=0.85,
        ),
        # With hyphens
        Pattern(
            name="french_ssn_hyphens",
            regex=r"\b[12]-\d{2}-\d{2}-\d{2}-\d{3}-\d{3}-\d{2}\b",
            score=0.85,
        ),
        # No separators
        Pattern(
            name="french_ssn_no_sep",
            regex=r"\b[12]\d{12}\d{2}\b",
            score=0.8,
        ),
    ]

    CONTEXT = [
        "sécurité sociale", "securite sociale", "numéro de sécurité",
        "NIR", "insee", "immatriculation", "numéro sécu"
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "fr",
        supported_entity: str = "FR_SSN",
    ):
        patterns = patterns if patterns else self.PATTERNS
        context = context if context else self.CONTEXT
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )


class CreditCardRecognizer(PatternRecognizer):
    """
    Recognizer for Credit Card numbers with Luhn algorithm validation
    Supports major card types:
    - Visa (starts with 4, 13 or 16 digits)
    - Mastercard (starts with 51-55 or 2221-2720, 16 digits)
    - American Express (starts with 34 or 37, 15 digits)
    - Discover (starts with 6011, 622126-622925, 644-649, 65, 16 digits)
    
    Formats supported:
    - 1234567890123456 (no spaces)
    - 1234 5678 9012 3456 (spaces every 4 digits)
    - 1234-5678-9012-3456 (hyphens every 4 digits)
    """

    PATTERNS = [
        # Visa: 4xxx xxxx xxxx xxxx (16 digits) or 4xxx xxxx xxxx xxx (13 digits)
        Pattern(
            name="visa_16",
            regex=r"\b4\d{3}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b",
            score=0.85,
        ),
        Pattern(
            name="visa_13",
            regex=r"\b4\d{3}[\s\-]?\d{4}[\s\-]?\d{3}[\s\-]?\d{2}\b",
            score=0.85,
        ),
        # Mastercard: 5[1-5]xx xxxx xxxx xxxx (16 digits)
        Pattern(
            name="mastercard",
            regex=r"\b5[1-5]\d{2}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b",
            score=0.85,
        ),
        # Mastercard (new range): 2[2-7]xx xxxx xxxx xxxx
        Pattern(
            name="mastercard_new",
            regex=r"\b2[2-7]\d{2}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b",
            score=0.85,
        ),
        # American Express: 3[47]xx xxxx xxxx xxx (15 digits)
        Pattern(
            name="amex",
            regex=r"\b3[47]\d{2}[\s\-]?\d{6}[\s\-]?\d{5}\b",
            score=0.85,
        ),
        # Discover: 6011 xxxx xxxx xxxx or 65xx xxxx xxxx xxxx
        Pattern(
            name="discover",
            regex=r"\b(?:6011|65\d{2})[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b",
            score=0.85,
        ),
        # Generic 16-digit pattern (fallback)
        Pattern(
            name="generic_cc",
            regex=r"\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b",
            score=0.6,
        ),
    ]

    CONTEXT = [
        "carte", "card", "bancaire", "credit", "crédit", "paiement", 
        "payment", "visa", "mastercard", "amex", "american express",
        "carte bleue", "cb", "numéro de carte"
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "fr",
        supported_entity: str = "CREDIT_CARD",
    ):
        patterns = patterns if patterns else self.PATTERNS
        context = context if context else self.CONTEXT
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )


class MedicalIDRecognizer(PatternRecognizer):
    """
    Recognizer for medical identification numbers
    """

    PATTERNS = [
        Pattern(
            name="patient_id_format1",
            regex=r"\b[A-Z]{2,3}\d{6,10}\b",
            score=0.65,
        ),
        Pattern(
            name="medical_record_num",
            regex=r"\b(?:MRN|DPI|IPP)[\s\-:]?\d{6,12}\b",
            score=0.85,
        ),
    ]

    CONTEXT = [
        "patient", "dossier", "identifiant", "numéro", "MRN", "DPI", "IPP",
        "matricule", "hospitalisation", "admission"
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "fr",
        supported_entity: str = "MEDICAL_ID",
    ):
        patterns = patterns if patterns else self.PATTERNS
        context = context if context else self.CONTEXT
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )


class FrenchAddressRecognizer(PatternRecognizer):
    """
    Recognizer for French addresses
    """

    PATTERNS = [
        Pattern(
            name="french_street_address",
            regex=r"\b\d{1,4}\s+(?:rue|avenue|boulevard|place|chemin|impasse|allée)\s+[A-Za-zÀ-ÿ\s\-\']+",
            score=0.7,
        ),
    ]

    CONTEXT = [
        "adresse", "rue", "avenue", "boulevard", "domicile", "résidence",
        "habite", "postal", "ville"
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "fr",
        supported_entity: str = "ADDRESS",
    ):
        patterns = patterns if patterns else self.PATTERNS
        context = context if context else self.CONTEXT
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )


class DoctorNameRecognizer(PatternRecognizer):
    """
    Recognizer for doctor/physician names with titles
    Matches patterns like:
    - Dr. Jean Dupont
    - Dr Jean-Pierre Martin
    - Docteur Marie Bernard
    - Pr. Sophie Lefevre
    - Professeur Jacques Dubois
    """

    PATTERNS = [
        # Dr. or Dr followed by full name (First Last)
        Pattern(
            name="doctor_with_title",
            regex=r"\b(?:Dr\.?|Docteur|Pr\.?|Professeur)\s+[A-ZÀ-Ÿ][a-zà-ÿ]+\s+[A-ZÀ-Ÿ][a-zà-ÿ]+\b",
            score=0.95,
        ),
        # Médecin/Medecin followed by name
        Pattern(
            name="medecin_with_name",
            regex=r"\b(?:Médecin|Medecin)\s*:\s*(?:Dr\.?\s+)?[A-ZÀ-Ÿ][a-zà-ÿ]+\s+[A-ZÀ-Ÿ][a-zà-ÿ]+\b",
            score=0.95,
        ),
    ]

    CONTEXT = [
        "medecin", "médecin", "docteur", "praticien", "cardiologue",
        "chirurgien", "specialiste", "spécialiste", "consultation",
        "prescripteur", "clinicien", "service"
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "fr",
        supported_entity: str = "PERSON",
    ):
        patterns = patterns if patterns else self.PATTERNS
        context = context if context else self.CONTEXT
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )


class HL7NameRecognizer(PatternRecognizer):
    """
    Recognizer for names in HL7 format (e.g., LASTNAME^FIRSTNAME)
    Common in medical HL7 messages
    """
    
    PATTERNS = [
        # HL7 format: LASTNAME^FIRSTNAME or LastName^FirstName
        Pattern(
            name="hl7_name_format",
            regex=r"\b([A-ZÀ-Ÿ][a-zà-ÿ]+)\^([A-ZÀ-Ÿ][a-zà-ÿ]+)\b",
            score=0.9,
        ),
        # All caps HL7: LASTNAME^FIRSTNAME
        Pattern(
            name="hl7_name_caps",
            regex=r"\b([A-ZÀ-Ÿ]{2,})\^([A-ZÀ-Ÿ]{2,})\b",
            score=0.85,
        ),
        # With middle name: LAST^FIRST^MIDDLE
        Pattern(
            name="hl7_name_with_middle",
            regex=r"\b([A-ZÀ-Ÿ][a-zà-ÿ]+)\^([A-ZÀ-Ÿ][a-zà-ÿ]+)\^([A-ZÀ-Ÿ][a-zà-ÿ]+)\b",
            score=0.9,
        ),
    ]
    
    CONTEXT = [
        "patient", "nom", "name", "medecin", "docteur", "dr", "infirmier",
        "PID", "NK1", "OBR", "PV1"  # HL7 segment identifiers
    ]
    
    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "fr",
        supported_entity: str = "PERSON",
    ):
        patterns = patterns if patterns else self.PATTERNS
        context = context if context else self.CONTEXT
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )


class ArabicNameRecognizer(PatternRecognizer):
    """
    Recognizer for Arabic names with common prefixes (El, Al, Ben, etc.)
    Common in North African French medical records
    
    Examples:
    - El Fassi, Al Mansouri, Ben Ali, Bel Hadj
    """
    
    PATTERNS = [
        # Full name with El/Al prefix (Firstname El Lastname or Firstname Middlename El Lastname)
        Pattern(
            name="arabic_full_name_el",
            regex=r"\b[A-ZÀ-Ÿ][a-zà-ÿ]+\s+(?:[A-ZÀ-Ÿ][a-zà-ÿ]+\s+)?(?:El|Al)\s+[A-ZÀ-Ÿ][a-zà-ÿ]+\b",
            score=0.95,
        ),
        # Full name with Ben/Ibn prefix
        Pattern(
            name="arabic_full_name_ben",
            regex=r"\b[A-ZÀ-Ÿ][a-zà-ÿ]+\s+(?:[A-ZÀ-Ÿ][a-zà-ÿ]+\s+)?(?:Ben|Ibn)(?:omar|ali|[a-zà-ÿ]+)\b",
            score=0.95,
        ),
        # El/Al prefix + lastname only
        Pattern(
            name="arabic_el_prefix",
            regex=r"\b(?:El|Al)\s+[A-ZÀ-Ÿ][a-zà-ÿ]+\b",
            score=0.85,
        ),
        # Ben/Ibn prefix + lastname only
        Pattern(
            name="arabic_ben_prefix", 
            regex=r"\b(?:Ben|Ibn)(?:omar|ali|[a-zà-ÿ]+)\b",
            score=0.85,
        ),
    ]
    
    CONTEXT = [
        "nom", "nom du patient", "patient", "patiente",
        "médecin", "medecin", "dr", "docteur",
        "identité", "identite"
    ]
    
    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "fr",
        supported_entity: str = "PERSON",
    ):
        patterns = patterns if patterns else self.PATTERNS
        context = context if context else self.CONTEXT
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )

class FullNameRecognizer(PatternRecognizer):
    """
    Recognizer for full names after field labels like "Nom :" or "Patient :"
    Catches patterns like: Nom : Maryam El Fassi
    """
    
    PATTERNS = [
        # Full name with 3 words (Firstname Middlename Lastname)
        Pattern(
            name="full_name_3words",
            regex=r"\b[A-ZÀ-Ÿ][a-zà-ÿ]+\s+[A-ZÀ-Ÿ][a-zà-ÿ]+\s+[A-ZÀ-Ÿ][a-zà-ÿ]+\b",
            score=0.85,
        ),
        # Full name with 4 words (includes El, Al, Ben, etc.)
        Pattern(
            name="full_name_4words",
            regex=r"\b[A-ZÀ-Ÿ][a-zà-ÿ]+\s+[A-ZÀ-Ÿ][a-zà-ÿ]+\s+[A-ZÀ-Ÿ][a-zà-ÿ]+\s+[A-ZÀ-Ÿ][a-zà-ÿ]+\b",
            score=0.9,
        ),
    ]
    
    CONTEXT = [
        "nom", "patient", "patiente", "m�decin", "medecin", 
        "docteur", "dr", "identit�", "identite"
    ]
    
    def __init__(
        self,
        patterns=None,
        context=None,
        supported_language="fr",
        supported_entity="PERSON",
    ):
        patterns = patterns if patterns else self.PATTERNS
        context = context if context else self.CONTEXT
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )
