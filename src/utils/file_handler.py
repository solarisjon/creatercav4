import os
import shutil
from pathlib import Path
from typing import List, Optional
import hashlib
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class FileHandler:
    """Handle file operations with security and validation"""
    
    def __init__(self, upload_dir: str, allowed_extensions: List[str], max_size_mb: int = 50):
        self.upload_dir = Path(upload_dir)
        self.allowed_extensions = [ext.lower() for ext in allowed_extensions]
        self.max_size_bytes = max_size_mb * 1024 * 1024
        
        # Create upload directory if it doesn't exist
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    def validate_file(self, file_path: Path) -> bool:
        """Validate file extension and size"""
        try:
            # Check if file exists
            if not file_path.exists():
                logger.error(f"File does not exist: {file_path}")
                return False
            
            # Check file extension
            if file_path.suffix.lower() not in self.allowed_extensions:
                logger.error(f"File extension not allowed: {file_path.suffix}")
                return False
            
            # Check file size
            file_size = file_path.stat().st_size
            if file_size > self.max_size_bytes:
                logger.error(f"File too large: {file_size} bytes (max: {self.max_size_bytes})")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating file {file_path}: {e}")
            return False
    
    def get_file_hash(self, file_path: Path) -> str:
        """Generate SHA256 hash of file"""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            logger.error(f"Error generating hash for {file_path}: {e}")
            return ""
    
    def save_uploaded_file(self, file_content: bytes, filename: str) -> Optional[Path]:
        """Save uploaded file to upload directory"""
        try:
            # Sanitize filename
            safe_filename = self._sanitize_filename(filename)
            file_path = self.upload_dir / safe_filename
            
            # Check if file already exists, add suffix if needed
            counter = 1
            original_path = file_path
            while file_path.exists():
                stem = original_path.stem
                suffix = original_path.suffix
                file_path = self.upload_dir / f"{stem}_{counter}{suffix}"
                counter += 1
            
            # Save file
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            # Validate saved file
            if not self.validate_file(file_path):
                file_path.unlink()  # Delete invalid file
                return None
            
            logger.info(f"File saved: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error saving file {filename}: {e}")
            return None
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename to prevent directory traversal and other issues"""
        # Remove path separators and other dangerous characters
        dangerous_chars = ['/', '\\', '..', '~', '|', '&', ';', '$', '`', '<', '>', '(', ')', '[', ']', '{', '}', '"', "'"]
        
        safe_filename = filename
        for char in dangerous_chars:
            safe_filename = safe_filename.replace(char, '_')
        
        # Limit filename length
        if len(safe_filename) > 255:
            name_part = safe_filename[:200]
            ext_part = safe_filename[-50:]
            safe_filename = name_part + ext_part
        
        return safe_filename
    
    def cleanup_old_files(self, days_old: int = 7):
        """Remove files older than specified days"""
        try:
            import time
            current_time = time.time()
            cutoff_time = current_time - (days_old * 24 * 60 * 60)
            
            deleted_count = 0
            for file_path in self.upload_dir.iterdir():
                if file_path.is_file():
                    file_mtime = file_path.stat().st_mtime
                    if file_mtime < cutoff_time:
                        file_path.unlink()
                        deleted_count += 1
                        logger.info(f"Deleted old file: {file_path}")
            
            logger.info(f"Cleanup completed. Deleted {deleted_count} old files.")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def get_file_info(self, file_path: Path) -> dict:
        """Get file information"""
        try:
            stat = file_path.stat()
            return {
                'name': file_path.name,
                'size': stat.st_size,
                'modified': stat.st_mtime,
                'extension': file_path.suffix,
                'hash': self.get_file_hash(file_path)
            }
        except Exception as e:
            logger.error(f"Error getting file info for {file_path}: {e}")
            return {}