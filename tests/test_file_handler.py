import pytest
from pathlib import Path
from src.utils.file_handler import FileHandler

class TestFileHandler:
    @pytest.fixture
    def file_handler(self, temp_dir):
        """Create FileHandler instance for testing"""
        upload_dir = temp_dir / "uploads"
        allowed_extensions = ['.pdf', '.txt', '.md']
        return FileHandler(str(upload_dir), allowed_extensions, max_size_mb=1)
    
    def test_init(self, file_handler, temp_dir):
        """Test FileHandler initialization"""
        assert file_handler.upload_dir == temp_dir / "uploads"
        assert file_handler.allowed_extensions == ['.pdf', '.txt', '.md']
        assert file_handler.max_size_bytes == 1024 * 1024
        assert file_handler.upload_dir.exists()
    
    def test_validate_file_success(self, file_handler, temp_dir):
        """Test successful file validation"""
        # Create a small test file
        test_file = temp_dir / "test.txt"
        test_file.write_text("Test content")
        
        assert file_handler.validate_file(test_file) is True
    
    def test_validate_file_not_exists(self, file_handler, temp_dir):
        """Test validation of non-existent file"""
        non_existent_file = temp_dir / "non_existent.txt"
        
        assert file_handler.validate_file(non_existent_file) is False
    
    def test_validate_file_wrong_extension(self, file_handler, temp_dir):
        """Test validation of file with wrong extension"""
        test_file = temp_dir / "test.exe"
        test_file.write_text("Test content")
        
        assert file_handler.validate_file(test_file) is False
    
    def test_validate_file_too_large(self, file_handler, temp_dir):
        """Test validation of file that's too large"""
        # Create a file larger than 1MB
        test_file = temp_dir / "large.txt"
        large_content = "x" * (1024 * 1024 + 1)  # 1MB + 1 byte
        test_file.write_text(large_content)
        
        assert file_handler.validate_file(test_file) is False
    
    def test_get_file_hash(self, file_handler, temp_dir):
        """Test file hash generation"""
        test_file = temp_dir / "test.txt"
        test_file.write_text("Test content")
        
        hash1 = file_handler.get_file_hash(test_file)
        hash2 = file_handler.get_file_hash(test_file)
        
        assert hash1 == hash2  # Same file should produce same hash
        assert len(hash1) == 64  # SHA256 hash length
    
    def test_get_file_hash_different_files(self, file_handler, temp_dir):
        """Test hash generation for different files"""
        file1 = temp_dir / "test1.txt"
        file2 = temp_dir / "test2.txt"
        
        file1.write_text("Content 1")
        file2.write_text("Content 2")
        
        hash1 = file_handler.get_file_hash(file1)
        hash2 = file_handler.get_file_hash(file2)
        
        assert hash1 != hash2
    
    def test_save_uploaded_file_success(self, file_handler, temp_dir):
        """Test successful file upload"""
        file_content = b"Test file content"
        filename = "test.txt"
        
        saved_path = file_handler.save_uploaded_file(file_content, filename)
        
        assert saved_path is not None
        assert saved_path.exists()
        assert saved_path.read_bytes() == file_content
    
    def test_save_uploaded_file_invalid_extension(self, file_handler, temp_dir):
        """Test file upload with invalid extension"""
        file_content = b"Test file content"
        filename = "test.exe"
        
        saved_path = file_handler.save_uploaded_file(file_content, filename)
        
        assert saved_path is None
    
    def test_save_uploaded_file_too_large(self, file_handler, temp_dir):
        """Test file upload that's too large"""
        large_content = b"x" * (1024 * 1024 + 1)  # 1MB + 1 byte
        filename = "large.txt"
        
        saved_path = file_handler.save_uploaded_file(large_content, filename)
        
        assert saved_path is None
    
    def test_save_uploaded_file_duplicate_name(self, file_handler, temp_dir):
        """Test file upload with duplicate filename"""
        file_content1 = b"Content 1"
        file_content2 = b"Content 2"
        filename = "test.txt"
        
        # Save first file
        saved_path1 = file_handler.save_uploaded_file(file_content1, filename)
        
        # Save second file with same name
        saved_path2 = file_handler.save_uploaded_file(file_content2, filename)
        
        assert saved_path1 != saved_path2
        assert saved_path1.exists()
        assert saved_path2.exists()
        assert saved_path1.read_bytes() == file_content1
        assert saved_path2.read_bytes() == file_content2
    
    def test_sanitize_filename(self, file_handler):
        """Test filename sanitization"""
        dangerous_filename = "../../../etc/passwd"
        safe_filename = file_handler._sanitize_filename(dangerous_filename)
        
        assert "../" not in safe_filename
        assert safe_filename == "___etc_passwd"
    
    def test_sanitize_filename_long(self, file_handler):
        """Test sanitization of very long filename"""
        long_filename = "a" * 300 + ".txt"
        safe_filename = file_handler._sanitize_filename(long_filename)
        
        assert len(safe_filename) <= 255
        assert safe_filename.endswith(".txt")
    
    def test_cleanup_old_files(self, file_handler, temp_dir):
        """Test cleanup of old files"""
        import time
        
        # Create old file
        old_file = file_handler.upload_dir / "old.txt"
        old_file.write_text("Old content")
        
        # Modify timestamp to make it old
        old_time = time.time() - (8 * 24 * 60 * 60)  # 8 days ago
        old_file.touch(times=(old_time, old_time))
        
        # Create new file
        new_file = file_handler.upload_dir / "new.txt"
        new_file.write_text("New content")
        
        # Run cleanup (files older than 7 days)
        file_handler.cleanup_old_files(days_old=7)
        
        assert not old_file.exists()
        assert new_file.exists()
    
    def test_get_file_info(self, file_handler, temp_dir):
        """Test getting file information"""
        test_file = temp_dir / "test.txt"
        test_content = "Test content"
        test_file.write_text(test_content)
        
        file_info = file_handler.get_file_info(test_file)
        
        assert file_info['name'] == 'test.txt'
        assert file_info['size'] == len(test_content)
        assert file_info['extension'] == '.txt'
        assert 'modified' in file_info
        assert 'hash' in file_info
        assert len(file_info['hash']) == 64  # SHA256 length
    
    def test_get_file_info_non_existent(self, file_handler, temp_dir):
        """Test getting info for non-existent file"""
        non_existent_file = temp_dir / "non_existent.txt"
        
        file_info = file_handler.get_file_info(non_existent_file)
        
        assert file_info == {}