import pytest
from datetime import datetime, timezone
from app.models.tryon_job import TryOnJob, JobStatus

class TestTryOnJobModel:
    """Test cases for TryOnJob model."""
    
    def test_tryon_job_creation(self, session, sample_user, sample_product):
        """Test creating a new try-on job."""
        job = TryOnJob(
            user_id=sample_user.id,
            product_id=sample_product.id,
            person_image_url="http://example.com/person.jpg",
            garment_image_url="http://example.com/garment.jpg",
            status=JobStatus.PENDING
        )
        session.add(job)
        session.commit()
        
        assert job.id is not None
        assert job.user_id == sample_user.id
        assert job.product_id == sample_product.id
        assert job.person_image_url == "http://example.com/person.jpg"
        assert job.garment_image_url == "http://example.com/garment.jpg"
        assert job.status == JobStatus.PENDING
        assert job.created_at is not None
        assert job.completed_at is None
        assert job.result_url is None
        assert job.error_message is None
    
    def test_job_status_enum(self):
        """Test JobStatus enum values."""
        assert JobStatus.PENDING.value == "PENDING"
        assert JobStatus.PROCESSING.value == "PROCESSING"
        assert JobStatus.DONE.value == "DONE"
        assert JobStatus.FAILED.value == "FAILED"
    
    def test_job_to_dict(self, sample_tryon_job):
        """Test job serialization."""
        job_dict = sample_tryon_job.to_dict()
        
        assert job_dict['id'] == sample_tryon_job.id
        assert job_dict['user_id'] == sample_tryon_job.user_id
        assert job_dict['product_id'] == sample_tryon_job.product_id
        assert job_dict['person_image_url'] == sample_tryon_job.person_image_url
        assert job_dict['garment_image_url'] == sample_tryon_job.garment_image_url
        assert job_dict['status'] == "PENDING"
        assert job_dict['result_url'] is None
        assert job_dict['error_message'] is None
        assert 'created_at' in job_dict
        assert job_dict['completed_at'] is None
    
    def test_job_completed_state(self, session, sample_tryon_job):
        """Test job in completed state."""
        sample_tryon_job.status = JobStatus.DONE
        sample_tryon_job.result_url = "results/123/456"
        sample_tryon_job.completed_at = datetime.now(timezone.utc)
        session.commit()
        
        job_dict = sample_tryon_job.to_dict()
        assert job_dict['status'] == "DONE"
        assert job_dict['result_url'] == "results/123/456"
        assert job_dict['completed_at'] is not None
    
    def test_job_failed_state(self, session, sample_tryon_job):
        """Test job in failed state."""
        sample_tryon_job.status = JobStatus.FAILED
        sample_tryon_job.error_message = "Model inference failed"
        sample_tryon_job.completed_at = datetime.now(timezone.utc)
        session.commit()
        
        job_dict = sample_tryon_job.to_dict()
        assert job_dict['status'] == "FAILED"
        assert job_dict['error_message'] == "Model inference failed"
        assert job_dict['completed_at'] is not None
    
    def test_job_repr(self, sample_tryon_job):
        """Test job string representation."""
        repr_str = repr(sample_tryon_job)
        assert f"<TryOnJob id={sample_tryon_job.id}" in repr_str
        assert "status=PENDING" in repr_str
    
    def test_job_relationships(self, session, sample_tryon_job):
        """Test job relationships."""
        # Refresh to get relationships
        session.refresh(sample_tryon_job)
        
        assert sample_tryon_job.user is not None
        assert sample_tryon_job.user.id == sample_tryon_job.user_id
        assert sample_tryon_job.product is not None
        assert sample_tryon_job.product.id == sample_tryon_job.product_id
    
    def test_job_without_product(self, session, sample_user):
        """Test job can exist without product reference."""
        job = TryOnJob(
            user_id=sample_user.id,
            product_id=None,  # No product reference
            person_image_url="http://example.com/person.jpg",
            garment_image_url="http://example.com/garment.jpg",
            status=JobStatus.PENDING
        )
        session.add(job)
        session.commit()
        
        assert job.product_id is None
        assert job.product is None
    
    def test_job_cascade_delete_with_user(self, session, sample_user, sample_product):
        """Test job is deleted when user is deleted."""
        job = TryOnJob(
            user_id=sample_user.id,
            product_id=sample_product.id,
            person_image_url="http://example.com/person.jpg",
            garment_image_url="http://example.com/garment.jpg",
            status=JobStatus.PENDING
        )
        session.add(job)
        session.commit()
        
        job_id = job.id
        
        # Delete user
        session.delete(sample_user)
        session.commit()
        
        # Job should be deleted
        deleted_job = session.query(TryOnJob).filter_by(id=job_id).first()
        assert deleted_job is None
    
    def test_job_product_set_null_on_delete(self, session, sample_user, sample_product):
        """Test job product_id is set to null when product is deleted."""
        job = TryOnJob(
            user_id=sample_user.id,
            product_id=sample_product.id,
            person_image_url="http://example.com/person.jpg",
            garment_image_url="http://example.com/garment.jpg",
            status=JobStatus.PENDING
        )
        session.add(job)
        session.commit()
        
        # Delete product
        session.delete(sample_product)
        session.commit()
        
        # Refresh job
        session.refresh(job)
        
        # Job should still exist but product_id should be null
        assert job.product_id is None