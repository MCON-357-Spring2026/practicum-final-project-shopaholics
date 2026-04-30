import io
import uuid
import logging
import threading
from datetime import datetime, timezone

import requests

logger = logging.getLogger(__name__)


def run_tryon_job(app, job_id: str) -> None:
    """Run in a background thread. Downloads result and saves to S3."""
    with app.app_context():
        from app.extensions import db
        from app.models.tryon_job import TryOnJob, JobStatus
        from app.services import fashn, s3

        job = db.session.get(TryOnJob, job_id)
        if not job:
            logger.error(f"TryOnJob {job_id} not found")
            return

        try:
            # ── Step 1: mark processing ──────────────────
            job.status = JobStatus.PROCESSING
            db.session.commit()

            # ── Step 2: submit to Fashn.ai ───────────────
            prediction_id = fashn.submit_tryon(
                job.person_image_url,
                job.garment_image_url,
            )
            job.fashn_prediction_id = prediction_id
            db.session.commit()

            # ── Step 3: poll until done ──────────────────
            result_image_url = fashn.poll_result(prediction_id)

            # ── Step 4: download result image ────────────
            img_response = requests.get(result_image_url, timeout=30)
            img_response.raise_for_status()
            img_bytes = img_response.content

            # ── Step 5: upload result to S3 ──────────────
            key = f"results/{job.user_id}/{uuid.uuid4()}.jpg"
            s3.upload_file(io.BytesIO(img_bytes), key, content_type="image/jpeg")

            # ── Step 6: mark done ─────────────────────────
            job.result_url = key
            job.status = JobStatus.DONE
            job.completed_at = datetime.now(timezone.utc)
            db.session.commit()

            logger.info(f"TryOnJob {job_id} completed → {key}")

        except Exception as e:
            logger.error(f"TryOnJob {job_id} failed: {e}")
            try:
                job.status = JobStatus.FAILED
                job.error_message = str(e)
                job.completed_at = datetime.now(timezone.utc)
                db.session.commit()
            except Exception:
                db.session.rollback()


def dispatch(app, job_id: str) -> None:
    """Spawn a daemon thread for a try-on job."""
    t = threading.Thread(target=run_tryon_job, args=(app, job_id), daemon=True)
    t.start()
