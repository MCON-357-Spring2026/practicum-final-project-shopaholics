import uuid
import logging
import threading
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


def run_tryon_job(app, job_id: str) -> None:
    """Run in a background thread: call Hugging Face, save result to Cloudinary."""
    with app.app_context():
        from app.extensions import db
        from app.models.tryon_job import TryOnJob, JobStatus
        from app.models.product import Product
        from app.services import huggingface, storage

        job = db.session.get(TryOnJob, job_id)
        if not job:
            logger.error(f"TryOnJob {job_id} not found")
            return

        try:
            # ── Step 1: mark processing ──────────────────
            job.status = JobStatus.PROCESSING
            db.session.commit()

            # A short garment description helps IDM-VTON; use the product title.
            description = "an item of clothing"
            if job.product_id:
                product = db.session.get(Product, job.product_id)
                if product and product.title:
                    description = product.title

            # ── Step 2: run the try-on model (blocking) ──
            result_path = huggingface.run_tryon(
                job.person_image_url,
                job.garment_image_url,
                description,
            )

            # ── Step 3: store result in Cloudinary ───────
            public_id = f"results/{job.user_id}/{uuid.uuid4()}"
            uploaded = storage.upload_image(result_path, public_id)

            # ── Step 4: mark done ─────────────────────────
            job.result_url = uploaded["public_id"]
            job.status = JobStatus.DONE
            job.completed_at = datetime.now(timezone.utc)
            db.session.commit()

            logger.info(f"TryOnJob {job_id} completed → {uploaded['public_id']}")

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
