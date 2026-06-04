import pytest
from datetime import datetime, timezone
from app.repositories import TryOnJobRepository
from app.models.tryon_job import TryOnJob, JobStatus

class TestTryOnJobRepository:
    """Test cases for TryOnJobRepository."""
    
    def test_create_job(self, session, sample_user, sample_product):
        """Test creating a new try-on job."""
        repo = TryOnJobRepository(session)
        
        job = repo.create_job(
            user_id=sample_user.id,
            product_id=sample_product.id,
            user_image_url="http://example.com/person.jpg",
            garment_image_url="http://example.com/garment.jpg"
        )
        
        assert job.id is not None
        assert job.user_id == sample_user.id
        assert job.product_id == sample_product.id
        assert job.person_image_url == "http://example.com/person.jpg"
        assert job.garment_image_url == "http://example.com/garment.jpg"
        assert job.status == JobStatus.PENDING
    
    def test_get_user_jobs(self, session, sample_user, sample_product):
        """Test getting user's jobs."""
        repo = TryOnJobRepository(session)
        
        # Create multiple jobs
        for i in range(5):
            repo.create_job(
                user_id=sample_user.id,
                product_id=sample_product.id,
                user_image_url=f"http://example.com/person{i}.jpg",
                garment_image_url=f"http://example.com/garment{i}.jpg"
            )
        
        # Get all jobs
        jobs = repo.get_user_jobs(sample_user.id)
        assert len(jobs) == 5
        
        # Test pagination
        jobs = repo.get_user_jobs(sample_user.id, limit=3)
        assert len(jobs) == 3
        
        jobs = repo.get_user_jobs(sample_user.id, limit=3, offset=3)
        assert len(jobs) == 2
    
    def test_get_user_job_by_id(self, session, sample_tryon_job, sample_user):
        """Test getting specific user job."""
        repo = TryOnJobRepository(session)
        
        # Get existing job
        job = repo.get_user_job_by_id(sample_user.id, sample_tryon_job.id)
        assert job is not None
        assert job.id == sample_tryon_job.id
        
        # Try to get job with wrong user_id
        job = repo.get_user_job_by_id("wrong-user-id", sample_tryon_job.id)
        assert job is None
        
        # Try to get non-existent job
        job = repo.get_user_job_by_id(sample_user.id, "non-existent-id")
        assert job is None
    
    def test_get_pending_jobs(self, session, sample_user, sample_product):
        """Test getting pending jobs."""
        repo = TryOnJobRepository(session)
        
        # Create jobs with different statuses
        pending1 = repo.create_job(
            user_id=sample_user.id,
            product_id=sample_product.id,
            user_image_url="http://example.com/1.jpg",
            garment_image_url="http://example.com/1.jpg"
        )
        
        processing = repo.create_job(
            user_id=sample_user.id,
            product_id=sample_product.id,
            user_image_url="http://example.com/2.jpg",
            garment_image_url="http://example.com/2.jpg"
        )
        repo.mark_as_processing(processing)
        
        pending2 = repo.create_job(
            user_id=sample_user.id,
            product_id=sample_product.id,
            user_image_url="http://example.com/3.jpg",
            garment_image_url="http://example.com/3.jpg"
        )
        
        # Get pending jobs
        pending_jobs = repo.get_pending_jobs()
        assert len(pending_jobs) == 2
        assert all(job.status == JobStatus.PENDING for job in pending_jobs)
        
        # Test with limit
        pending_jobs = repo.get_pending_jobs(limit=1)
        assert len(pending_jobs) == 1
    
    def test_update_job_status(self, session, sample_tryon_job):
        """Test updating job status."""
        repo = TryOnJobRepository(session)
        
        # Update to processing
        updated = repo.update_job_status(sample_tryon_job, JobStatus.PROCESSING)
        assert updated.status == JobStatus.PROCESSING
        assert updated.completed_at is not None
        
        # Update to done with result
        updated = repo.update_job_status(
            sample_tryon_job, 
            JobStatus.DONE,
            result_url="results/123/456"
        )
        assert updated.status == JobStatus.DONE
        assert updated.result_url == "results/123/456"
        
        # Update to failed with error
        updated = repo.update_job_status(
            sample_tryon_job,
            JobStatus.FAILED,
            error_message="Model error"
        )
        assert updated.status == JobStatus.FAILED
        assert updated.error_message == "Model error"
    
    def test_mark_as_processing(self, session, sample_tryon_job):
        """Test marking job as processing."""
        repo = TryOnJobRepository(session)
        
        updated = repo.mark_as_processing(sample_tryon_job)
        assert updated.status == JobStatus.PROCESSING
    
    def test_mark_as_completed(self, session, sample_tryon_job):
        """Test marking job as completed."""
        repo = TryOnJobRepository(session)
        
        updated = repo.mark_as_completed(sample_tryon_job, "results/abc/def")
        assert updated.status == JobStatus.DONE
        assert updated.result_url == "results/abc/def"
        assert updated.completed_at is not None
    
    def test_mark_as_failed(self, session, sample_tryon_job):
        """Test marking job as failed."""
        repo = TryOnJobRepository(session)
        
        updated = repo.mark_as_failed(sample_tryon_job, "API error")
        assert updated.status == JobStatus.FAILED
        assert updated.error_message == "API error"
        assert updated.completed_at is not None
    
    def test_count_user_jobs(self, session, sample_user, sample_product):
        """Test counting user jobs."""
        repo = TryOnJobRepository(session)
        
        # Initially should be 0
        count = repo.count_user_jobs(sample_user.id)
        assert count == 0
        
        # Create some jobs
        for i in range(3):
            repo.create_job(
                user_id=sample_user.id,
                product_id=sample_product.id,
                user_image_url=f"http://example.com/{i}.jpg",
                garment_image_url=f"http://example.com/{i}.jpg"
            )
        
        count = repo.count_user_jobs(sample_user.id)
        assert count == 3
    
    def test_get_jobs_by_status(self, session, sample_user, sample_product):
        """Test getting jobs by status."""
        repo = TryOnJobRepository(session)
        
        # Create jobs with different statuses
        for status in [JobStatus.PENDING, JobStatus.PENDING, JobStatus.PROCESSING, JobStatus.DONE]:
            job = repo.create_job(
                user_id=sample_user.id,
                product_id=sample_product.id,
                user_image_url="http://example.com/test.jpg",
                garment_image_url="http://example.com/test.jpg"
            )
            if status != JobStatus.PENDING:
                repo.update_job_status(job, status)
        
        pending = repo.get_jobs_by_status(JobStatus.PENDING)
        assert len(pending) == 2
        
        processing = repo.get_jobs_by_status(JobStatus.PROCESSING)
        assert len(processing) == 1
        
        done = repo.get_jobs_by_status(JobStatus.DONE)
        assert len(done) == 1
    
    def test_delete_user_job(self, session, sample_user, sample_tryon_job):
        """Test deleting user job."""
        repo = TryOnJobRepository(session)
        
        job_id = sample_tryon_job.id
        
        # Delete the job
        result = repo.delete_user_job(sample_user.id, job_id)
        assert result is True
        
        # Verify it's deleted
        job = repo.get_user_job_by_id(sample_user.id, job_id)
        assert job is None
        
        # Try to delete non-existent job
        result = repo.delete_user_job(sample_user.id, "non-existent")
        assert result is False