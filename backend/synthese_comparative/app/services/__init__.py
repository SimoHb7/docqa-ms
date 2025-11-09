"""
Services package initialization
"""
from app.services.database import (
    get_engine,
    get_connection,
    get_document_by_id,
    get_anonymized_content,
    get_multiple_documents,
    get_multiple_anonymized_contents,
    test_connection,
)
from app.services.anonymization_service import (
    AnonymizationService,
    anonymization_service,
)

__all__ = [
    # Database functions
    "get_engine",
    "get_connection",
    "get_document_by_id",
    "get_anonymized_content",
    "get_multiple_documents",
    "get_multiple_anonymized_contents",
    "test_connection",
    # Anonymization service
    "AnonymizationService",
    "anonymization_service",
]
