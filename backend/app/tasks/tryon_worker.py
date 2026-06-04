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
        from app.repositories import TryOnJobRepository, ProductRepository

        job_repo = TryOnJobRepository()
        job = job_repo.get_by_id(job_id)
        if not job:
            logger.error(f"TryOnJob {job_id} not found")
            return

        try:
            # ── Step 1: mark processing ──────────────────
            job_repo.mark_as_processing(job)

            # A short garment description helps IDM-VTON; use the product title.
            description = "an item of clothing"
            category = ""
            if job.product_id:
                product_repo = ProductRepository()
                product = product_repo.get_by_id(job.product_id)
                if product:
                    if product.title:
                        description = product.title
                    category = (product.category or "").lower()

            # ── Step 2: run the try-on model (blocking) ──
            # Dresses look much better on a full-body model; everything else
            # uses IDM-VTON (best for upper-body garments).
            is_dress = "dress" in category or category == "overall"

            if is_dress:
                try:
                    result_path = huggingface.run_tryon_fullbody(
                        job.person_image_url, job.garment_image_url, category="Dress"
                    )
                except Exception as e:
                    logger.warning(
                        f"Full-body model failed ({e}); falling back to IDM-VTON"
                    )
                    result_path = huggingface.run_tryon(
                        job.person_image_url, job.garment_image_url, description
                    )
            else:
                result_path = huggingface.run_tryon(
                    job.person_image_url, job.garment_image_url, description
                )

            # ── Step 3: store result in Cloudinary ───────
            public_id = f"results/{job.user_id}/{uuid.uuid4()}"
            uploaded = storage.upload_image(result_path, public_id)

            # ── Step 4: mark done ─────────────────────────
            job_repo.mark_as_completed(job, uploaded["public_id"])

            logger.info(f"TryOnJob {job_id} completed → {uploaded['public_id']}")

        except Exception as e:
            logger.error(f"TryOnJob {job_id} failed: {e}")
            try:
                job_repo.mark_as_failed(job, str(e))
            except Exception:
                db.session.rollback()


def dispatch(app, job_id: str) -> None:
    """Spawn a daemon thread for a try-on job."""
    t = threading.Thread(target=run_tryon_job, args=(app, job_id), daemon=True)
    t.start()
