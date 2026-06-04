from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.tryon_job import TryOnJob, JobStatus
from app.repositories.base import BaseRepository

class TryOnJobRepository(BaseRepository[TryOnJob]):
    model = TryOnJob

    def __init__(self, session: Session = None):
        super().__init__(session)

    def create_job(self, user_id: str, product_id: str, user_image_url: str, 
                  garment_image_url: str) -> TryOnJob:
        job = TryOnJob(
            user_id=user_id,
            product_id=product_id,
            person_image_url=user_image_url,
            garment_image_url=garment_image_url,
            status=JobStatus.PENDING
        )
        return self.save(job)

    def get_user_jobs(self, user_id: str, limit: int = None, offset: int = None) -> List[TryOnJob]:
        query = self.session.query(TryOnJob).filter(
            TryOnJob.user_id == user_id
        ).order_by(TryOnJob.created_at.desc())
        
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
        
        return query.all()

    def get_user_job_by_id(self, user_id: str, job_id: str) -> Optional[TryOnJob]:
        return self.session.query(TryOnJob).filter(
            and_(
                TryOnJob.id == job_id,
                TryOnJob.user_id == user_id
            )
        ).first()

    def get_pending_jobs(self, limit: int = None) -> List[TryOnJob]:
        query = self.session.query(TryOnJob).filter(
            TryOnJob.status == JobStatus.PENDING
        ).order_by(TryOnJob.created_at.asc())
        
        if limit:
            query = query.limit(limit)
        
        return query.all()

    def update_job_status(self, job: TryOnJob, status: JobStatus, 
                         result_url: str = None, error_message: str = None) -> TryOnJob:
        job.status = status
        job.completed_at = datetime.now(timezone.utc)
        
        if result_url:
            job.result_url = result_url
        if error_message:
            job.error_message = error_message
        
        return self.save(job)

    def mark_as_processing(self, job: TryOnJob) -> TryOnJob:
        job.status = JobStatus.PROCESSING
        return self.save(job)

    def mark_as_completed(self, job: TryOnJob, result_url: str) -> TryOnJob:
        return self.update_job_status(job, JobStatus.DONE, result_url=result_url)

    def mark_as_failed(self, job: TryOnJob, error_message: str) -> TryOnJob:
        return self.update_job_status(job, JobStatus.FAILED, error_message=error_message)

    def count_user_jobs(self, user_id: str) -> int:
        return self.session.query(TryOnJob).filter(
            TryOnJob.user_id == user_id
        ).count()

    def get_jobs_by_status(self, status: JobStatus, limit: int = None) -> List[TryOnJob]:
        query = self.session.query(TryOnJob).filter(TryOnJob.status == status)
        if limit:
            query = query.limit(limit)
        return query.all()

    def delete_user_job(self, user_id: str, job_id: str) -> bool:
        job = self.get_user_job_by_id(user_id, job_id)
        if job:
            return self.delete(job)
        return False