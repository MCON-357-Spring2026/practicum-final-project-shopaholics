from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models.tryon_job import TryOnJob, JobStatus
from app.models.product import Product
from app.services import storage
from app.tasks import tryon_worker
from app.repositories import TryOnJobRepository

tryon_bp = Blueprint("tryon", __name__)


# ── Generate try-on job ───────────────────────────────────
@tryon_bp.post("/generate")
@jwt_required()
def generate():
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    person_image_url = data.get("person_image_url")
    garment_image_url = data.get("garment_image_url")
    product_id = data.get("product_id")

    if not person_image_url or not garment_image_url:
        return jsonify({"error": "person_image_url and garment_image_url are required"}), 400

    job_repo = TryOnJobRepository()
    job = job_repo.create_job(
        user_id=user_id,
        product_id=product_id,
        user_image_url=person_image_url,
        garment_image_url=garment_image_url
    )

    tryon_worker.dispatch(current_app._get_current_object(), job.id)

    return jsonify({"job_id": job.id, "status": job.status.value}), 202


# ── Poll job status ───────────────────────────────────────
@tryon_bp.get("/jobs/<string:job_id>")
@jwt_required()
def get_job(job_id: str):
    user_id = get_jwt_identity()

    job_repo = TryOnJobRepository()
    job = job_repo.get_user_job_by_id(user_id, job_id)

    if not job:
        return jsonify({"error": "Job not found"}), 404

    payload = job.to_dict()

    if job.status == JobStatus.DONE and job.result_url:
        payload["result_url"] = storage.get_url(job.result_url)

    return jsonify(payload), 200


# ── History ───────────────────────────────────────────────
@tryon_bp.get("/history")
@jwt_required()
def history():
    user_id = get_jwt_identity()
    page = int(request.args.get("page", 1))
    per_page = min(int(request.args.get("per_page", 10)), 50)

    job_repo = TryOnJobRepository()
    offset = (page - 1) * per_page
    jobs_list = job_repo.get_user_jobs(user_id, limit=per_page, offset=offset)
    total = job_repo.count_user_jobs(user_id)
    
    jobs = []
    for job in jobs_list:
        payload = job.to_dict()
        if job.status == JobStatus.DONE and job.result_url:
            payload["result_url"] = storage.get_url(job.result_url)
        jobs.append(payload)

    pages = (total + per_page - 1) // per_page  # Calculate total pages
    
    return jsonify({
        "jobs": jobs,
        "total": total,
        "page": page,
        "pages": pages,
    }), 200


# ── Delete a job ──────────────────────────────────────────
@tryon_bp.delete("/jobs/<string:job_id>")
@jwt_required()
def delete_job(job_id: str):
    user_id = get_jwt_identity()

    job_repo = TryOnJobRepository()
    job = job_repo.get_user_job_by_id(user_id, job_id)

    if not job:
        return jsonify({"error": "Job not found"}), 404

    if job.result_url:
        storage.delete_file(job.result_url)

    job_repo.delete(job)

    return jsonify({"message": "Job deleted"}), 200
