"""
Image storage backed by Cloudinary (replaces the old AWS S3 service).

Cloudinary images are served from public CDN URLs, so there are no
pre-signed URLs to generate — we store the Cloudinary ``public_id`` in the
database and build a delivery URL from it on demand.
"""
import cloudinary
import cloudinary.uploader
import cloudinary.utils
from flask import current_app


def _configure() -> None:
    cloudinary.config(
        cloud_name=current_app.config["CLOUDINARY_CLOUD_NAME"],
        api_key=current_app.config["CLOUDINARY_API_KEY"],
        api_secret=current_app.config["CLOUDINARY_API_SECRET"],
        secure=True,
    )


def upload_image(file_or_path, public_id: str) -> dict:
    """
    Upload an image to Cloudinary.

    ``file_or_path`` may be a file-like object (e.g. Flask's ``file.stream``),
    raw bytes, a local file path, or a remote URL.

    Returns ``{"public_id": ..., "url": ...}``.
    """
    _configure()
    result = cloudinary.uploader.upload(
        file_or_path,
        public_id=public_id,
        resource_type="image",
        overwrite=True,
    )
    return {"public_id": result["public_id"], "url": result["secure_url"]}


def get_url(public_id: str) -> str:
    """Build a public delivery URL for a stored Cloudinary public_id."""
    _configure()
    url, _ = cloudinary.utils.cloudinary_url(public_id, resource_type="image", secure=True)
    return url


def delete_file(public_id: str) -> None:
    """Delete an image from Cloudinary by its public_id (best-effort)."""
    _configure()
    try:
        cloudinary.uploader.destroy(public_id, resource_type="image")
    except Exception:
        pass
