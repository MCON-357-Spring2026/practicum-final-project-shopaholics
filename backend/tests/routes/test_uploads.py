import pytest
import io
from unittest.mock import patch, Mock

class TestUploadRoutes:
    """Test cases for upload routes."""
    
    @patch('app.services.storage.upload_image')
    @patch('app.services.storage.get_url')
    def test_upload_image_success(self, mock_get_url, mock_upload, client, auth_headers):
        """Test successful image upload."""
        mock_upload.return_value = {
            'public_id': 'uploads/user123/image456',
            'secure_url': 'https://cloudinary.com/uploads/user123/image456.jpg'
        }
        mock_get_url.return_value = 'https://cloudinary.com/uploads/user123/image456.jpg'
        
        # Create a test image file
        data = {
            'image': (io.BytesIO(b'fake image data'), 'test_image.jpg')
        }
        
        response = client.post(
            '/api/uploads/image',
            headers=auth_headers,
            data=data,
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['url'] == 'https://cloudinary.com/uploads/user123/image456.jpg'
        assert json_data['public_id'] == 'uploads/user123/image456'
        
        mock_upload.assert_called_once()
    
    def test_upload_no_file(self, client, auth_headers):
        """Test upload with no file provided."""
        response = client.post(
            '/api/uploads/image',
            headers=auth_headers
        )
        
        assert response.status_code == 400
        assert 'No image provided' in response.get_json()['error']
    
    def test_upload_empty_filename(self, client, auth_headers):
        """Test upload with empty filename."""
        data = {
            'image': (io.BytesIO(b''), '')  # Empty filename
        }
        
        response = client.post(
            '/api/uploads/image',
            headers=auth_headers,
            data=data,
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 400
        assert 'No image provided' in response.get_json()['error']
    
    def test_upload_invalid_file_type(self, client, auth_headers):
        """Test upload with invalid file type."""
        data = {
            'image': (io.BytesIO(b'not an image'), 'test.txt')
        }
        
        response = client.post(
            '/api/uploads/image',
            headers=auth_headers,
            data=data,
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 400
        assert 'Invalid file type' in response.get_json()['error']
    
    def test_upload_file_too_large(self, client, auth_headers):
        """Test upload with file exceeding size limit."""
        # Create a large file (> 10MB)
        large_data = b'x' * (10 * 1024 * 1024 + 1)
        data = {
            'image': (io.BytesIO(large_data), 'large_image.jpg')
        }
        
        response = client.post(
            '/api/uploads/image',
            headers=auth_headers,
            data=data,
            content_type='multipart/form-data'
        )
        
        # Flask might handle this at a lower level, so status could be 413
        assert response.status_code in [400, 413]
    
    def test_upload_allowed_extensions(self, client, auth_headers):
        """Test upload with various allowed file extensions."""
        allowed_extensions = ['jpg', 'jpeg', 'png', 'gif', 'webp']
        
        for ext in allowed_extensions:
            with patch('app.services.storage.upload_image') as mock_upload:
                mock_upload.return_value = {
                    'public_id': f'uploads/test.{ext}',
                    'secure_url': f'https://cloudinary.com/test.{ext}'
                }
                
                data = {
                    'image': (io.BytesIO(b'image data'), f'test.{ext}')
                }
                
                response = client.post(
                    '/api/uploads/image',
                    headers=auth_headers,
                    data=data,
                    content_type='multipart/form-data'
                )
                
                assert response.status_code == 200
    
    @patch('app.services.storage.upload_image')
    def test_upload_storage_error(self, mock_upload, client, auth_headers):
        """Test upload when storage service fails."""
        mock_upload.side_effect = Exception('Storage service error')
        
        data = {
            'image': (io.BytesIO(b'image data'), 'test.jpg')
        }
        
        response = client.post(
            '/api/uploads/image',
            headers=auth_headers,
            data=data,
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 500
        assert 'Upload failed' in response.get_json()['error']
    
    def test_upload_unauthenticated(self, client):
        """Test upload without authentication."""
        data = {
            'image': (io.BytesIO(b'image data'), 'test.jpg')
        }
        
        response = client.post(
            '/api/uploads/image',
            data=data,
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 401
    
    @patch('app.services.storage.upload_image')
    @patch('app.services.storage.get_url')
    def test_upload_filename_sanitization(self, mock_get_url, mock_upload, 
                                        client, auth_headers):
        """Test that uploaded filenames are properly sanitized."""
        mock_upload.return_value = {
            'public_id': 'uploads/user123/sanitized_name',
            'secure_url': 'https://cloudinary.com/uploads/user123/sanitized_name.jpg'
        }
        mock_get_url.return_value = 'https://cloudinary.com/uploads/user123/sanitized_name.jpg'
        
        # Upload with problematic filename
        data = {
            'image': (io.BytesIO(b'image data'), '../../../etc/passwd.jpg')
        }
        
        response = client.post(
            '/api/uploads/image',
            headers=auth_headers,
            data=data,
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 200
        
        # Verify the upload was called with a safe path
        call_args = mock_upload.call_args
        assert '../' not in str(call_args)