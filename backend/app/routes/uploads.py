import uuid
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services import s3

uploads_bp = Blueprint("uploads", __name__)

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
MAX_BYTES = 10 * 1024 * 1024  # 10 MB


def _allowed(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ── Upload person photo ──────────────────────────────────
@uploads_bp.post("/person")
@jwt_required()
def upload_person():
    user_id = get_jwt_identity()

    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]

    if not file.filename or not _allowed(file.filename):
        return jsonify({"error": "Invalid file type. Allowed: jpg, jpeg, png, webp"}), 400

    file.seek(0, 2)
    size = file.tell()
    file.seek(0)

    if size > MAX_BYTES:
        return jsonify({"error": "File too large. Max 10 MB"}), 413

    ext = file.filename.rsplit(".", 1)[1].lower()
    key = f"persons/{user_id}/{uuid.uuid4()}.{ext}"
    content_type = file.content_type or f"image/{ext}"

    s3.upload_file(file.stream, key, content_type)
    url = s3.get_presigned_url(key)

    return jsonify({
        "key": key,
        "url": url,
    }), 201


# ── Delete an uploaded image ─────────────────────────────
@uploads_bp.delete("/<path:key>")
@jwt_required()
def delete_upload(key: str):
    user_id = get_jwt_identity()

    # Users may only delete their own uploads
    if not key.startswith(f"persons/{user_id}/"):
        return jsonify({"error": "Forbidden"}), 403

    s3.delete_file(key)
    return jsonify({"message": "Deleted"}), 200
