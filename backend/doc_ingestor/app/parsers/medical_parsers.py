"""
Medical format parsers for HL7 and FHIR documents
"""
import json
from typing import Dict, Any, Optional
from datetime import datetime


class HL7Parser:
    """
    Parser for HL7 v2.x messages
    Supports common message types: ADT, ORU, ORM, etc.
    """
    
    @staticmethod
    def parse(content: str) -> Dict[str, Any]:
        """
        Parse HL7 v2.x message
        
        Args:
            content: Raw HL7 message content
            
        Returns:
            Parsed HL7 data as dictionary
        """
        try:
            segments = content.strip().split('\n')
            parsed_data = {
                "message_type": None,
                "patient": {},
                "observations": [],
                "orders": [],
                "segments": {},
                "raw_text": content
            }
            
            for segment in segments:
                if not segment.strip():
                    continue
                    
                fields = segment.split('|')
                segment_type = fields[0] if fields else None
                
                if not segment_type:
                    continue
                
                # Store raw segment
                if segment_type not in parsed_data["segments"]:
                    parsed_data["segments"][segment_type] = []
                parsed_data["segments"][segment_type].append(fields)
                
                # Parse common segments
                if segment_type == "MSH":  # Message Header
                    parsed_data["message_type"] = fields[8] if len(fields) > 8 else None
                    parsed_data["message_timestamp"] = fields[6] if len(fields) > 6 else None
                    
                elif segment_type == "PID":  # Patient Identification
                    parsed_data["patient"] = {
                        "id": fields[3] if len(fields) > 3 else None,
                        "name": fields[5] if len(fields) > 5 else None,
                        "dob": fields[7] if len(fields) > 7 else None,
                        "sex": fields[8] if len(fields) > 8 else None,
                        "address": fields[11] if len(fields) > 11 else None,
                    }
                    
                elif segment_type == "OBX":  # Observation Result
                    observation = {
                        "id": fields[1] if len(fields) > 1 else None,
                        "type": fields[2] if len(fields) > 2 else None,
                        "identifier": fields[3] if len(fields) > 3 else None,
                        "value": fields[5] if len(fields) > 5 else None,
                        "units": fields[6] if len(fields) > 6 else None,
                        "reference_range": fields[7] if len(fields) > 7 else None,
                        "status": fields[11] if len(fields) > 11 else None,
                    }
                    parsed_data["observations"].append(observation)
                    
                elif segment_type == "ORC":  # Common Order
                    order = {
                        "control": fields[1] if len(fields) > 1 else None,
                        "order_id": fields[2] if len(fields) > 2 else None,
                        "status": fields[5] if len(fields) > 5 else None,
                    }
                    parsed_data["orders"].append(order)
            
            return parsed_data
            
        except Exception as e:
            return {
                "error": f"Failed to parse HL7: {str(e)}",
                "raw_text": content
            }
    
    @staticmethod
    def to_readable_text(parsed_data: Dict[str, Any]) -> str:
        """
        Convert parsed HL7 data to human-readable text
        
        Args:
            parsed_data: Parsed HL7 dictionary
            
        Returns:
            Human-readable text representation
        """
        lines = ["=== HL7 MESSAGE ===\n"]
        
        if parsed_data.get("message_type"):
            lines.append(f"Message Type: {parsed_data['message_type']}")
        
        if parsed_data.get("message_timestamp"):
            lines.append(f"Timestamp: {parsed_data['message_timestamp']}\n")
        
        # Patient information
        if parsed_data.get("patient"):
            lines.append("\n--- PATIENT INFORMATION ---")
            patient = parsed_data["patient"]
            if patient.get("id"):
                lines.append(f"Patient ID: {patient['id']}")
            if patient.get("name"):
                lines.append(f"Name: {patient['name']}")
            if patient.get("dob"):
                lines.append(f"Date of Birth: {patient['dob']}")
            if patient.get("sex"):
                lines.append(f"Sex: {patient['sex']}")
            if patient.get("address"):
                lines.append(f"Address: {patient['address']}")
        
        # Observations/Lab Results
        if parsed_data.get("observations"):
            lines.append("\n--- OBSERVATIONS/LAB RESULTS ---")
            for i, obs in enumerate(parsed_data["observations"], 1):
                lines.append(f"\nObservation {i}:")
                if obs.get("identifier"):
                    lines.append(f"  Test: {obs['identifier']}")
                if obs.get("value"):
                    value_str = f"  Value: {obs['value']}"
                    if obs.get("units"):
                        value_str += f" {obs['units']}"
                    lines.append(value_str)
                if obs.get("reference_range"):
                    lines.append(f"  Reference Range: {obs['reference_range']}")
                if obs.get("status"):
                    lines.append(f"  Status: {obs['status']}")
        
        # Orders
        if parsed_data.get("orders"):
            lines.append("\n--- ORDERS ---")
            for i, order in enumerate(parsed_data["orders"], 1):
                lines.append(f"\nOrder {i}:")
                if order.get("order_id"):
                    lines.append(f"  Order ID: {order['order_id']}")
                if order.get("control"):
                    lines.append(f"  Control: {order['control']}")
                if order.get("status"):
                    lines.append(f"  Status: {order['status']}")
        
        return "\n".join(lines)


class FHIRParser:
    """
    Parser for FHIR (Fast Healthcare Interoperability Resources) documents
    Supports FHIR JSON format (R4, R5)
    """
    
    @staticmethod
    def parse(content: str) -> Dict[str, Any]:
        """
        Parse FHIR JSON resource
        
        Args:
            content: FHIR JSON content
            
        Returns:
            Parsed FHIR data
        """
        try:
            fhir_data = json.loads(content)
            
            parsed_data = {
                "resource_type": fhir_data.get("resourceType"),
                "id": fhir_data.get("id"),
                "patient": {},
                "observations": [],
                "conditions": [],
                "medications": [],
                "encounters": [],
                "procedures": [],
                "raw_data": fhir_data,
                "raw_text": content
            }
            
            resource_type = fhir_data.get("resourceType")
            
            # Parse based on resource type
            if resource_type == "Patient":
                parsed_data["patient"] = FHIRParser._parse_patient(fhir_data)
                
            elif resource_type == "Observation":
                parsed_data["observations"].append(FHIRParser._parse_observation(fhir_data))
                
            elif resource_type == "Condition":
                parsed_data["conditions"].append(FHIRParser._parse_condition(fhir_data))
                
            elif resource_type == "MedicationRequest" or resource_type == "MedicationStatement":
                parsed_data["medications"].append(FHIRParser._parse_medication(fhir_data))
                
            elif resource_type == "Encounter":
                parsed_data["encounters"].append(FHIRParser._parse_encounter(fhir_data))
                
            elif resource_type == "Procedure":
                parsed_data["procedures"].append(FHIRParser._parse_procedure(fhir_data))
                
            elif resource_type == "Bundle":
                # Parse bundle entries
                entries = fhir_data.get("entry", [])
                for entry in entries:
                    resource = entry.get("resource", {})
                    entry_type = resource.get("resourceType")
                    
                    if entry_type == "Patient":
                        parsed_data["patient"] = FHIRParser._parse_patient(resource)
                    elif entry_type == "Observation":
                        parsed_data["observations"].append(FHIRParser._parse_observation(resource))
                    elif entry_type == "Condition":
                        parsed_data["conditions"].append(FHIRParser._parse_condition(resource))
                    elif entry_type in ["MedicationRequest", "MedicationStatement"]:
                        parsed_data["medications"].append(FHIRParser._parse_medication(resource))
                    elif entry_type == "Encounter":
                        parsed_data["encounters"].append(FHIRParser._parse_encounter(resource))
                    elif entry_type == "Procedure":
                        parsed_data["procedures"].append(FHIRParser._parse_procedure(resource))
            
            return parsed_data
            
        except json.JSONDecodeError as e:
            return {
                "error": f"Invalid FHIR JSON: {str(e)}",
                "raw_text": content
            }
        except Exception as e:
            return {
                "error": f"Failed to parse FHIR: {str(e)}",
                "raw_text": content
            }
    
    @staticmethod
    def _parse_patient(resource: Dict) -> Dict[str, Any]:
        """Parse Patient resource"""
        patient = {
            "id": resource.get("id"),
            "identifier": [],
            "name": None,
            "gender": resource.get("gender"),
            "birth_date": resource.get("birthDate"),
            "address": [],
            "telecom": []
        }
        
        # Identifiers
        for identifier in resource.get("identifier", []):
            patient["identifier"].append({
                "system": identifier.get("system"),
                "value": identifier.get("value")
            })
        
        # Name
        names = resource.get("name", [])
        if names:
            name = names[0]
            given = " ".join(name.get("given", []))
            family = name.get("family", "")
            patient["name"] = f"{given} {family}".strip()
        
        # Address
        for address in resource.get("address", []):
            lines = address.get("line", [])
            city = address.get("city", "")
            postal_code = address.get("postalCode", "")
            patient["address"].append(f"{' '.join(lines)}, {city} {postal_code}".strip())
        
        # Telecom
        for telecom in resource.get("telecom", []):
            patient["telecom"].append({
                "system": telecom.get("system"),
                "value": telecom.get("value")
            })
        
        return patient
    
    @staticmethod
    def _parse_observation(resource: Dict) -> Dict[str, Any]:
        """Parse Observation resource"""
        obs = {
            "id": resource.get("id"),
            "status": resource.get("status"),
            "code": None,
            "value": None,
            "unit": None,
            "effective_datetime": resource.get("effectiveDateTime"),
            "interpretation": []
        }
        
        # Code
        code = resource.get("code", {})
        coding = code.get("coding", [])
        if coding:
            obs["code"] = coding[0].get("display") or coding[0].get("code")
        
        # Value
        if "valueQuantity" in resource:
            value_qty = resource["valueQuantity"]
            obs["value"] = value_qty.get("value")
            obs["unit"] = value_qty.get("unit")
        elif "valueString" in resource:
            obs["value"] = resource["valueString"]
        elif "valueCodeableConcept" in resource:
            value_cc = resource["valueCodeableConcept"]
            coding = value_cc.get("coding", [])
            if coding:
                obs["value"] = coding[0].get("display")
        
        # Interpretation
        for interp in resource.get("interpretation", []):
            coding = interp.get("coding", [])
            if coding:
                obs["interpretation"].append(coding[0].get("display"))
        
        return obs
    
    @staticmethod
    def _parse_condition(resource: Dict) -> Dict[str, Any]:
        """Parse Condition resource"""
        condition = {
            "id": resource.get("id"),
            "clinical_status": None,
            "code": None,
            "onset_datetime": resource.get("onsetDateTime"),
            "recorded_date": resource.get("recordedDate")
        }
        
        # Clinical status
        clinical_status = resource.get("clinicalStatus", {})
        coding = clinical_status.get("coding", [])
        if coding:
            condition["clinical_status"] = coding[0].get("code")
        
        # Code
        code = resource.get("code", {})
        coding = code.get("coding", [])
        if coding:
            condition["code"] = coding[0].get("display") or coding[0].get("code")
        
        return condition
    
    @staticmethod
    def _parse_medication(resource: Dict) -> Dict[str, Any]:
        """Parse MedicationRequest or MedicationStatement"""
        medication = {
            "id": resource.get("id"),
            "status": resource.get("status"),
            "medication": None,
            "dosage": []
        }
        
        # Medication code
        med_concept = resource.get("medicationCodeableConcept", {})
        coding = med_concept.get("coding", [])
        if coding:
            medication["medication"] = coding[0].get("display") or coding[0].get("code")
        
        # Dosage
        for dosage in resource.get("dosageInstruction", []):
            medication["dosage"].append({
                "text": dosage.get("text"),
                "timing": dosage.get("timing", {}).get("code", {}).get("text")
            })
        
        return medication
    
    @staticmethod
    def _parse_encounter(resource: Dict) -> Dict[str, Any]:
        """Parse Encounter resource"""
        return {
            "id": resource.get("id"),
            "status": resource.get("status"),
            "class": resource.get("class", {}).get("code"),
            "period_start": resource.get("period", {}).get("start"),
            "period_end": resource.get("period", {}).get("end")
        }
    
    @staticmethod
    def _parse_procedure(resource: Dict) -> Dict[str, Any]:
        """Parse Procedure resource"""
        procedure = {
            "id": resource.get("id"),
            "status": resource.get("status"),
            "code": None,
            "performed_datetime": resource.get("performedDateTime")
        }
        
        code = resource.get("code", {})
        coding = code.get("coding", [])
        if coding:
            procedure["code"] = coding[0].get("display") or coding[0].get("code")
        
        return procedure
    
    @staticmethod
    def to_readable_text(parsed_data: Dict[str, Any]) -> str:
        """
        Convert parsed FHIR data to human-readable text
        
        Args:
            parsed_data: Parsed FHIR dictionary
            
        Returns:
            Human-readable text representation
        """
        lines = ["=== FHIR RESOURCE ===\n"]
        
        if parsed_data.get("resource_type"):
            lines.append(f"Resource Type: {parsed_data['resource_type']}")
        
        if parsed_data.get("id"):
            lines.append(f"Resource ID: {parsed_data['id']}\n")
        
        # Patient
        if parsed_data.get("patient") and parsed_data["patient"]:
            lines.append("\n--- PATIENT INFORMATION ---")
            patient = parsed_data["patient"]
            if patient.get("name"):
                lines.append(f"Name: {patient['name']}")
            if patient.get("gender"):
                lines.append(f"Gender: {patient['gender']}")
            if patient.get("birth_date"):
                lines.append(f"Birth Date: {patient['birth_date']}")
            if patient.get("identifier"):
                for ident in patient["identifier"]:
                    lines.append(f"Identifier: {ident.get('value')} ({ident.get('system')})")
        
        # Observations
        if parsed_data.get("observations"):
            lines.append("\n--- OBSERVATIONS ---")
            for i, obs in enumerate(parsed_data["observations"], 1):
                lines.append(f"\nObservation {i}:")
                if obs.get("code"):
                    lines.append(f"  Test: {obs['code']}")
                if obs.get("value"):
                    value_str = f"  Value: {obs['value']}"
                    if obs.get("unit"):
                        value_str += f" {obs['unit']}"
                    lines.append(value_str)
                if obs.get("effective_datetime"):
                    lines.append(f"  Date: {obs['effective_datetime']}")
                if obs.get("status"):
                    lines.append(f"  Status: {obs['status']}")
        
        # Conditions
        if parsed_data.get("conditions"):
            lines.append("\n--- CONDITIONS/DIAGNOSES ---")
            for i, cond in enumerate(parsed_data["conditions"], 1):
                lines.append(f"\nCondition {i}:")
                if cond.get("code"):
                    lines.append(f"  Diagnosis: {cond['code']}")
                if cond.get("clinical_status"):
                    lines.append(f"  Status: {cond['clinical_status']}")
                if cond.get("onset_datetime"):
                    lines.append(f"  Onset: {cond['onset_datetime']}")
        
        # Medications
        if parsed_data.get("medications"):
            lines.append("\n--- MEDICATIONS ---")
            for i, med in enumerate(parsed_data["medications"], 1):
                lines.append(f"\nMedication {i}:")
                if med.get("medication"):
                    lines.append(f"  Medication: {med['medication']}")
                if med.get("status"):
                    lines.append(f"  Status: {med['status']}")
                for dosage in med.get("dosage", []):
                    if dosage.get("text"):
                        lines.append(f"  Dosage: {dosage['text']}")
        
        # Procedures
        if parsed_data.get("procedures"):
            lines.append("\n--- PROCEDURES ---")
            for i, proc in enumerate(parsed_data["procedures"], 1):
                lines.append(f"\nProcedure {i}:")
                if proc.get("code"):
                    lines.append(f"  Procedure: {proc['code']}")
                if proc.get("status"):
                    lines.append(f"  Status: {proc['status']}")
                if proc.get("performed_datetime"):
                    lines.append(f"  Performed: {proc['performed_datetime']}")
        
        # Encounters
        if parsed_data.get("encounters"):
            lines.append("\n--- ENCOUNTERS ---")
            for i, enc in enumerate(parsed_data["encounters"], 1):
                lines.append(f"\nEncounter {i}:")
                if enc.get("class"):
                    lines.append(f"  Type: {enc['class']}")
                if enc.get("status"):
                    lines.append(f"  Status: {enc['status']}")
                if enc.get("period_start"):
                    lines.append(f"  Start: {enc['period_start']}")
                if enc.get("period_end"):
                    lines.append(f"  End: {enc['period_end']}")
        
        return "\n".join(lines)


def detect_and_parse_medical_format(content: str, file_extension: str) -> tuple[str, Dict[str, Any]]:
    """
    Detect and parse medical format (HL7 or FHIR)
    
    Args:
        content: File content
        file_extension: File extension (hl7, fhir, json, xml)
        
    Returns:
        Tuple of (readable_text, parsed_data)
    """
    # Try to detect format
    if file_extension == "hl7" or content.startswith("MSH|"):
        # HL7 v2.x format
        parsed = HL7Parser.parse(content)
        readable_text = HL7Parser.to_readable_text(parsed)
        return readable_text, parsed
        
    elif file_extension in ["fhir", "json"]:
        # Try FHIR JSON
        try:
            json_data = json.loads(content)
            if "resourceType" in json_data:
                # It's FHIR
                parsed = FHIRParser.parse(content)
                readable_text = FHIRParser.to_readable_text(parsed)
                return readable_text, parsed
        except:
            pass
    
    # Fallback: return as-is
    return content, {"raw_text": content, "format": "unknown"}
