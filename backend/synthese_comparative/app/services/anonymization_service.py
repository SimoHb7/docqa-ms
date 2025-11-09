"""
Anonymization Service for Synthese Comparative
Provides high-level functions to retrieve and work with anonymized medical documents
"""
from typing import List, Dict, Any, Optional
import structlog

from app.services.database import (
    get_document_by_id,
    get_anonymized_content,
    get_multiple_documents,
    get_multiple_anonymized_contents
)

logger = structlog.get_logger(__name__)


class AnonymizationService:
    """
    Service to handle retrieval and processing of anonymized documents
    """
    
    @staticmethod
    async def get_anonymized_document(document_id: str) -> Optional[Dict[str, Any]]:
        """
        Get document with anonymized content
        
        Args:
            document_id: UUID of the document
            
        Returns:
            Dictionary with document metadata and anonymized content
            None if document not found or not anonymized
        """
        try:
            # Fetch document metadata
            document = await get_document_by_id(document_id)
            if not document:
                logger.warning("Document not found", document_id=document_id)
                return None
            
            # Check if document is anonymized
            if not document.get("is_anonymized"):
                logger.warning("Document not anonymized", document_id=document_id)
                # Return document with original content as fallback
                return {
                    "document_id": document["id"],
                    "filename": document["filename"],
                    "file_type": document["file_type"],
                    "content": document["content"],
                    "is_anonymized": False,
                    "pii_entities": [],
                    "metadata": document.get("metadata"),
                }
            
            # Fetch anonymized content
            anonymized = await get_anonymized_content(document_id)
            if not anonymized:
                logger.warning("Anonymized content not found", document_id=document_id)
                # Fallback to original content
                return {
                    "document_id": document["id"],
                    "filename": document["filename"],
                    "file_type": document["file_type"],
                    "content": document["content"],
                    "is_anonymized": False,
                    "pii_entities": [],
                    "metadata": document.get("metadata"),
                }
            
            # Combine document metadata with anonymized content
            return {
                "document_id": document["id"],
                "filename": document["filename"],
                "file_type": document["file_type"],
                "content": anonymized["anonymized_content"],
                "is_anonymized": True,
                "pii_entities": anonymized.get("pii_entities", []),
                "processing_time_ms": anonymized.get("processing_time_ms"),
                "metadata": document.get("metadata"),
                "created_at": document.get("created_at"),
            }
            
        except Exception as e:
            logger.error("Failed to get anonymized document", document_id=document_id, error=str(e))
            raise
    
    @staticmethod
    async def get_anonymized_documents_bulk(document_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Get multiple documents with anonymized content in bulk
        
        Args:
            document_ids: List of document UUIDs
            
        Returns:
            List of dictionaries with document metadata and anonymized content
        """
        try:
            if not document_ids:
                return []
            
            logger.info("Fetching anonymized documents in bulk", count=len(document_ids))
            
            # Fetch all documents and anonymizations in parallel
            documents = await get_multiple_documents(document_ids)
            anonymizations = await get_multiple_anonymized_contents(document_ids)
            
            # Create lookup dictionary for anonymizations
            anon_lookup = {a["document_id"]: a for a in anonymizations}
            
            # Combine documents with their anonymizations
            results = []
            for doc in documents:
                doc_id = doc["id"]
                anonymized = anon_lookup.get(doc_id)
                
                if anonymized:
                    results.append({
                        "document_id": doc_id,
                        "filename": doc["filename"],
                        "file_type": doc["file_type"],
                        "content": anonymized["anonymized_content"],
                        "is_anonymized": True,
                        "pii_entities": anonymized.get("pii_entities", []),
                        "processing_time_ms": anonymized.get("processing_time_ms"),
                        "metadata": doc.get("metadata"),
                        "created_at": doc.get("created_at"),
                    })
                else:
                    # Fallback to original content if no anonymization found
                    logger.warning("No anonymization found for document", document_id=doc_id)
                    results.append({
                        "document_id": doc_id,
                        "filename": doc["filename"],
                        "file_type": doc["file_type"],
                        "content": doc["content"],
                        "is_anonymized": False,
                        "pii_entities": [],
                        "metadata": doc.get("metadata"),
                        "created_at": doc.get("created_at"),
                    })
            
            logger.info("Successfully fetched anonymized documents", 
                       requested=len(document_ids), 
                       found=len(results))
            
            return results
            
        except Exception as e:
            logger.error("Failed to get anonymized documents bulk", error=str(e))
            raise
    
    @staticmethod
    async def extract_patient_timeline_data(documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract and structure data for patient timeline synthesis
        
        Args:
            documents: List of anonymized documents
            
        Returns:
            Structured data for timeline generation
        """
        timeline_data = {
            "documents": [],
            "total_documents": len(documents),
            "has_anonymized": any(d.get("is_anonymized") for d in documents),
        }
        
        for doc in documents:
            timeline_data["documents"].append({
                "id": doc["document_id"],
                "filename": doc["filename"],
                "content": doc["content"],
                "is_anonymized": doc.get("is_anonymized", False),
                "pii_count": len(doc.get("pii_entities", [])),
                "created_at": doc.get("created_at"),
            })
        
        return timeline_data
    
    @staticmethod
    async def extract_comparison_data(documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract and structure data for patient comparison synthesis
        
        Args:
            documents: List of anonymized documents
            
        Returns:
            Structured data for comparison generation
        """
        comparison_data = {
            "documents": [],
            "total_documents": len(documents),
            "has_anonymized": any(d.get("is_anonymized") for d in documents),
        }
        
        for doc in documents:
            comparison_data["documents"].append({
                "id": doc["document_id"],
                "filename": doc["filename"],
                "content": doc["content"],
                "is_anonymized": doc.get("is_anonymized", False),
                "pii_entities": doc.get("pii_entities", []),
                "file_type": doc.get("file_type"),
            })
        
        return comparison_data
    
    @staticmethod
    async def extract_summary_data(document: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract and structure data for document summary synthesis
        
        Args:
            document: Anonymized document
            
        Returns:
            Structured data for summary generation
        """
        return {
            "document_id": document["document_id"],
            "filename": document["filename"],
            "content": document["content"],
            "is_anonymized": document.get("is_anonymized", False),
            "pii_entities": document.get("pii_entities", []),
            "word_count": len(document["content"].split()) if document.get("content") else 0,
            "metadata": document.get("metadata"),
        }


# Singleton instance
anonymization_service = AnonymizationService()
