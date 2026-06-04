import pytest
from unittest.mock import patch, Mock
from app.models.tryon_job import JobStatus

class TestTryOnRoutes:
    """Test cases for try-on routes."""
    
    @patch('app.tasks.tryon_worker.dispatch')
    def test_generate_tryon_success(self, mock_dispatch, client, auth_headers, sample_user):
        """Test successful try-on job generation."""
        response = client.post('/api/tryon/generate', 
            headers=auth_headers,
            json={
                'person_image_url': 'http://example.com/person.jpg',
                'garment_image_url': 'http://example.com/garment.jpg',
                'product_id': 'product123'
            }
        )
        
        assert response.status_code == 202
        data = response.get_json()
        assert 'job_id' in data
        assert data['status'] == 'PENDING'
        
        # Verify dispatch was called
        mock_dispatch.assert_called_once()
    
    def test_generate_tryon_missing_fields(self, client, auth_headers):
        """Test try-on generation with missing required fields."""
        # Missing person_image_url
        response = client.post('/api/tryon/generate',
            headers=auth_headers,
            json={
                'garment_image_url': 'http://example.com/garment.jpg'
            }
        )
        
        assert response.status_code == 400
        assert 'person_image_url and garment_image_url are required' in response.get_json()['error']
        
        # Missing garment_image_url
        response = client.post('/api/tryon/generate',
            headers=auth_headers,
            json={
                'person_image_url': 'http://example.com/person.jpg'
            }
        )
        
        assert response.status_code == 400
    
    def test_generate_tryon_unauthenticated(self, client):
        """Test try-on generation without authentication."""
        response = client.post('/api/tryon/generate', json={
            'person_image_url': 'http://example.com/person.jpg',
            'garment_image_url': 'http://example.com/garment.jpg'
        })
        
        assert response.status_code == 401
    
    def test_get_job_success(self, client, auth_headers, sample_tryon_job):
        """Test getting job status."""
        response = client.get(
            f'/api/tryon/jobs/{sample_tryon_job.id}',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['id'] == sample_tryon_job.id
        assert data['status'] == 'PENDING'
    
    @patch('app.services.storage.get_url')
    def test_get_job_completed(self, mock_get_url, client, auth_headers, 
                              session, sample_tryon_job):
        """Test getting completed job with result URL."""
        # Mark job as done
        sample_tryon_job.status = JobStatus.DONE
        sample_tryon_job.result_url = 'results/123/456'
        session.commit()
        
        mock_get_url.return_value = 'https://cloudinary.com/results/123/456.jpg'
        
        response = client.get(
            f'/api/tryon/jobs/{sample_tryon_job.id}',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'DONE'
        assert data['result_url'] == 'https://cloudinary.com/results/123/456.jpg'
        
        mock_get_url.assert_called_once_with('results/123/456')
    
    def test_get_job_not_found(self, client, auth_headers):
        """Test getting non-existent job."""
        response = client.get(
            '/api/tryon/jobs/nonexistent-id',
            headers=auth_headers
        )
        
        assert response.status_code == 404
        assert 'Job not found' in response.get_json()['error']
    
    def test_get_job_wrong_user(self, client, auth_headers, session, sample_tryon_job, sample_user):
        """Test getting job that belongs to different user."""
        # Create another user
        from app.models.user import User
        other_user = User(email='other@test.com', password_hash='hash')
        session.add(other_user)
        session.commit()
        
        # Change job owner
        sample_tryon_job.user_id = other_user.id
        session.commit()
        
        response = client.get(
            f'/api/tryon/jobs/{sample_tryon_job.id}',
            headers=auth_headers  # Using original user's token
        )
        
        assert response.status_code == 404
        assert 'Job not found' in response.get_json()['error']
    
    def test_history_success(self, client, auth_headers, session, sample_user, sample_product):
        """Test getting user's try-on history."""
        # Create multiple jobs
        from app.models.tryon_job import TryOnJob
        for i in range(5):
            job = TryOnJob(
                user_id=sample_user.id,
                product_id=sample_product.id,
                person_image_url=f'http://example.com/person{i}.jpg',
                garment_image_url=f'http://example.com/garment{i}.jpg',
                status=JobStatus.DONE
            )
            session.add(job)
        session.commit()
        
        response = client.get('/api/tryon/history', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['jobs']) == 5
        assert data['total'] == 5
        assert data['page'] == 1
        assert data['pages'] == 1
    
    def test_history_pagination(self, client, auth_headers, session, sample_user, sample_product):
        """Test history pagination."""
        # Create 15 jobs
        from app.models.tryon_job import TryOnJob
        for i in range(15):
            job = TryOnJob(
                user_id=sample_user.id,
                product_id=sample_product.id,
                person_image_url=f'http://example.com/person{i}.jpg',
                garment_image_url=f'http://example.com/garment{i}.jpg'
            )
            session.add(job)
        session.commit()
        
        # Get first page
        response = client.get('/api/tryon/history?page=1&per_page=10', headers=auth_headers)
        data = response.get_json()
        assert len(data['jobs']) == 10
        assert data['total'] == 15
        assert data['page'] == 1
        assert data['pages'] == 2
        
        # Get second page
        response = client.get('/api/tryon/history?page=2&per_page=10', headers=auth_headers)
        data = response.get_json()
        assert len(data['jobs']) == 5
        assert data['page'] == 2
    
    @patch('app.services.storage.delete_file')
    def test_delete_job_success(self, mock_delete_file, client, auth_headers, 
                               session, sample_tryon_job):
        """Test deleting a try-on job."""
        # Set a result URL
        sample_tryon_job.result_url = 'results/123/456'
        session.commit()
        
        response = client.delete(
            f'/api/tryon/jobs/{sample_tryon_job.id}',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert response.get_json()['message'] == 'Job deleted'
        
        # Verify file deletion was called
        mock_delete_file.assert_called_once_with('results/123/456')
        
        # Verify job is deleted
        from app.models.tryon_job import TryOnJob
        deleted_job = session.query(TryOnJob).filter_by(id=sample_tryon_job.id).first()
        assert deleted_job is None
    
    def test_delete_job_not_found(self, client, auth_headers):
        """Test deleting non-existent job."""
        response = client.delete(
            '/api/tryon/jobs/nonexistent-id',
            headers=auth_headers
        )
        
        assert response.status_code == 404
        assert 'Job not found' in response.get_json()['error']
    
    def test_delete_job_wrong_user(self, client, auth_headers, session, sample_tryon_job):
        """Test deleting job that belongs to different user."""
        # Create another user
        from app.models.user import User
        other_user = User(email='other@test.com', password_hash='hash')
        session.add(other_user)
        session.commit()
        
        # Change job owner
        sample_tryon_job.user_id = other_user.id
        session.commit()
        
        response = client.delete(
            f'/api/tryon/jobs/{sample_tryon_job.id}',
            headers=auth_headers
        )
        
        assert response.status_code == 404