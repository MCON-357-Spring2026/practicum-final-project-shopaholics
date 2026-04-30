from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models.tryon_job import TryOnJob, JobStatus
from app.models.product import Product
from app.services import s3
from app.tasks import tryon_worker

tryon_bp = Blueprint("tryon", __name__)


# ── Generate try-on job ───────────────────────────────────
@tryon_bp.post("/generate")
@jwt_required()
def generate():
    user_id = get_jwt_identity()
    data = request.get_json()

    person_image_url = data.get("person_image_url")
    garment_image_url = data.get("garment_image_url")
    product_id = data.get("product_id")

    if not person_image_url or not garment_image_url:
        return jsonify({"error": "person_image_url and garment_image_url are required"}), 400

    job = TryOnJob(
        user_id=user_id,
        product_id=product_id,
        person_image_url=person_image_url,
        garment_image_url=garment_image_url,
        status=JobStatus.PENDING,
    )
    db.session.add(job)
    db.session.commit()

    tryon_worker.dispatch(current_app._get_current_object(), job.id)

    return jsonify({"job_id": job.id, "status": job.status.value}), 202


# ── Poll job status ───────────────────────────────────────
@tryon_bp.get("/jobs/<string:job_id>")
@jwt_required()
def get_job(job_id: str):
    user_id = get_jwt_identity()

    job = db.session.get(TryOnJob, job_id)

    if not job or job.user_id != user_id:
        return jsonify({"error": "Job not found"}), 404

    payload = job.to_dict()

    if job.status == JobStatus.DONE and job.result_url:
        payload["result_url"] = s3.get_presigned_url(job.result_url)

    return jsonify(payload), 200


# ── History ───────────────────────────────────────────────
@tryon_bp.get("/history")
@jwt_required()
def history():
    user_id = get_jwt_identity()
    page = int(request.args.get("page", 1))
    per_page = min(int(request.args.get("per_page", 10)), 50)

    pagination = (
        TryOnJob.query
        .filter_by(user_id=user_id)
        .order_by(TryOnJob.created_at.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )

    jobs = []
    for job in pagination.items:
        payload = job.to_dict()
        if job.status == JobStatus.DONE and job.result_url:
            payload["result_url"] = s3.get_presigned_url(job.result_url)
        jobs.append(payload)

    return jsonify({
        "jobs": jobs,
        "total": pagination.total,
        "page": page,
        "pages": pagination.pages,
    }), 200


# ── Delete a job ──────────────────────────────────────────
@tryon_bp.delete("/jobs/<string:job_id>")
@jwt_required()
def delete_job(job_id: str):
    user_id = get_jwt_identity()

    job = db.session.get(TryOnJob, job_id)

    if not job or job.user_id != user_id:
        return jsonify({"error": "Job not found"}), 404

    if job.result_url:
        s3.delete_file(job.result_url)

    db.session.delete(job)
    db.session.commit()

    return jsonify({"message": "Job deleted"}), 200
