import json
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.models.schemas import HandwrittenDocument

logger = logging.getLogger(__name__)


class HandwrittenDocumentStorage:
    """
    Storage service for managing handwritten document metadata.
    Uses JSON files for simple persistence.
    """
    
    def __init__(self):
        self.storage_dir = Path("app/data/handwritten")
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.storage_dir / "metadata.json"
        logger.info("HandwrittenDocumentStorage initialized.")
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Load metadata from JSON file."""
        if not self.metadata_file.exists():
            return {}
        
        try:
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading metadata: {e}")
            return {}
    
    def _save_metadata(self, metadata: Dict[str, Any]) -> None:
        """Save metadata to JSON file."""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving metadata: {e}")
    
    def store_document_metadata(self, task_id: str, group_id: str, original_filename: str) -> None:
        """Store initial metadata for a handwritten document."""
        metadata = self._load_metadata()
        
        document_data = {
            "task_id": task_id,
            "group_id": group_id,
            "original_filename": original_filename,
            "processed_filename": None,
            "status": "PENDING",
            "upload_timestamp": datetime.now().isoformat(),
            "error_message": None
        }
        
        metadata[task_id] = document_data
        self._save_metadata(metadata)
        logger.info(f"Stored metadata for task {task_id}")
    
    def update_document_status(self, task_id: str, result: Dict[str, Any]) -> None:
        """Update document metadata with processing results."""
        metadata = self._load_metadata()
        
        if task_id in metadata:
            metadata[task_id].update({
                "status": result.get("status", "UNKNOWN"),
                "processed_filename": result.get("processed_filename"),
                "error_message": result.get("error_message")
            })
            self._save_metadata(metadata)
            logger.info(f"Updated metadata for task {task_id}")
        else:
            logger.warning(f"Task {task_id} not found in metadata")
    
    def get_document(self, task_id: str) -> Optional[HandwrittenDocument]:
        """Get a specific handwritten document by task ID."""
        metadata = self._load_metadata()
        
        if task_id in metadata:
            doc_data = metadata[task_id]
            return HandwrittenDocument(**doc_data)
        
        return None
    
    def get_documents_by_group(self, group_id: str) -> List[HandwrittenDocument]:
        """Get all handwritten documents for a specific group."""
        metadata = self._load_metadata()
        documents = []
        
        for task_id, doc_data in metadata.items():
            if doc_data.get("group_id") == group_id:
                documents.append(HandwrittenDocument(**doc_data))
        
        # Sort by upload timestamp (newest first)
        documents.sort(key=lambda x: x.upload_timestamp, reverse=True)
        return documents
    
    def delete_document(self, task_id: str) -> bool:
        """Delete a handwritten document and its metadata."""
        metadata = self._load_metadata()
        
        if task_id in metadata:
            # Delete files
            group_id = metadata[task_id]["group_id"]
            task_dir = self.storage_dir / group_id / task_id
            
            if task_dir.exists():
                import shutil
                try:
                    shutil.rmtree(task_dir)
                    logger.info(f"Deleted directory {task_dir}")
                except Exception as e:
                    logger.error(f"Error deleting directory {task_dir}: {e}")
            
            # Remove from metadata
            del metadata[task_id]
            self._save_metadata(metadata)
            logger.info(f"Deleted metadata for task {task_id}")
            return True
        
        logger.warning(f"Task {task_id} not found for deletion")
        return False
    
    def get_file_path(self, task_id: str, file_type: str = "processed") -> Optional[Path]:
        """Get the file path for a document."""
        metadata = self._load_metadata()
        
        if task_id not in metadata:
            return None
        
        doc_data = metadata[task_id]
        group_id = doc_data["group_id"]
        task_dir = self.storage_dir / group_id / task_id
        
        if file_type == "processed" and doc_data.get("processed_filename"):
            return task_dir / doc_data["processed_filename"]
        elif file_type == "original":
            return task_dir / f"original_{doc_data['original_filename']}"
        
        return None


# Global instance
_handwritten_storage_instance: Optional[HandwrittenDocumentStorage] = None


def get_handwritten_storage() -> HandwrittenDocumentStorage:
    """Get the global handwritten storage instance."""
    global _handwritten_storage_instance
    if _handwritten_storage_instance is None:
        _handwritten_storage_instance = HandwrittenDocumentStorage()
    return _handwritten_storage_instance 