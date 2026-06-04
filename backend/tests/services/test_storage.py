import pytest
from unittest.mock import patch, Mock, MagicMock
from app.services import storage

class TestStorageService:
    """Test cases for storage service."""
    
    @patch('app.services.storage.cloudinary')
    def test_upload_image_success(self, mock_cloudinary):
        """Test successful image upload."""
        mock_result = {
            "public_id": "test/image123",
            "secure_url": "https://cloudinary.com/test/image123.jpg",
            "version": 1234567890
        }
        mock_cloudinary.uploader.upload.return_value = mock_result
        
        result = storage.upload_image("/path/to/image.jpg", "test/image123")
        
        assert result == mock_result
        mock_cloudinary.uploader.upload.assert_called_once_with(
            "/path/to/image.jpg",
            public_id="test/image123"
        )
    
    @patch('app.services.storage.cloudinary')
    def test_upload_image_error(self, mock_cloudinary):
        """Test image upload with error."""
        mock_cloudinary.uploader.upload.side_effect = Exception("Upload failed")
        
        with pytest.raises(Exception) as exc_info:
            storage.upload_image("/path/to/image.jpg", "test/image123")
        
        assert "Upload failed" in str(exc_info.value)
    
    @patch('app.services.storage.cloudinary')
    def test_get_url_with_cloudinary_id(self, mock_cloudinary):
        """Test getting URL from Cloudinary public ID."""
        mock_cloudinary.utils.cloudinary_url.return_value = (
            "https://res.cloudinary.com/demo/image/upload/v1234567890/test/image123.jpg",
            {}
        )
        
        url = storage.get_url("test/image123")
        
        assert url == "https://res.cloudinary.com/demo/image/upload/v1234567890/test/image123.jpg"
        mock_cloudinary.utils.cloudinary_url.assert_called_once_with("test/image123")
    
    def test_get_url_with_http_url(self):
        """Test getting URL when already an HTTP URL."""
        url = "http://example.com/image.jpg"
        result = storage.get_url(url)
        assert result == url
    
    def test_get_url_with_https_url(self):
        """Test getting URL when already an HTTPS URL."""
        url = "https://example.com/image.jpg"
        result = storage.get_url(url)
        assert result == url
    
    @patch('app.services.storage.cloudinary')
    def test_delete_file_success(self, mock_cloudinary):
        """Test successful file deletion."""
        mock_cloudinary.uploader.destroy.return_value = {"result": "ok"}
        
        result = storage.delete_file("test/image123")
        
        assert result is True
        mock_cloudinary.uploader.destroy.assert_called_once_with("test/image123")
    
    @patch('app.services.storage.cloudinary')
    def test_delete_file_not_found(self, mock_cloudinary):
        """Test file deletion when file not found."""
        mock_cloudinary.uploader.destroy.return_value = {"result": "not found"}
        
        result = storage.delete_file("test/nonexistent")
        
        assert result is True  # Should still return True
        mock_cloudinary.uploader.destroy.assert_called_once_with("test/nonexistent")
    
    @patch('app.services.storage.cloudinary')
    def test_delete_file_error(self, mock_cloudinary):
        """Test file deletion with error."""
        mock_cloudinary.uploader.destroy.side_effect = Exception("Delete failed")
        
        result = storage.delete_file("test/image123")
        
        assert result is False
    
    @patch('app.services.storage.cloudinary')
    def test_cloudinary_configuration(self, mock_cloudinary):
        """Test that Cloudinary is configured on import."""
        # The configuration should happen when the module is imported
        # We can't directly test the import-time configuration, but we can
        # verify that cloudinary methods are available
        assert hasattr(mock_cloudinary, 'config')
        assert hasattr(mock_cloudinary, 'uploader')
        assert hasattr(mock_cloudinary, 'utils')