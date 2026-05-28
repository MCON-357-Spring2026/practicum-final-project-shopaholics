"""
Virtual try-on via a Hugging Face Space (replaces the old Fashn.ai service).

The default Space is CatVTON (``zhengchong/CatVTON``). Spaces are Gradio apps,
so we call them with ``gradio_client`` rather than a raw REST endpoint. The
call is synchronous — it blocks until the model finishes — which is fine
because it runs inside the background try-on worker thread.

If the Space's API signature changes, open its page on huggingface.co, click
"Use via API", and adjust HF_TRYON_SPACE / HF_TRYON_API_NAME (and the predict
arguments below) to match.
"""
import logging

from flask import current_app
from gradio_client import Client, handle_file

logger = logging.getLogger(__name__)


def run_tryon(person_image_url: str, garment_image_url: str) -> str:
    """
    Send the person photo + garment image to the try-on Space and return a
    local filepath to the generated result image (downloaded by gradio_client).
    Raises on failure.
    """
    space = current_app.config["HF_TRYON_SPACE"]
    api_name = current_app.config["HF_TRYON_API_NAME"]
    token = current_app.config.get("HUGGINGFACE_API_TOKEN") or None

    logger.info(f"Connecting to HF Space {space}")
    client = Client(space, hf_token=token)

    # CatVTON's person input is a Gradio ImageEditor → expects a dict.
    result = client.predict(
        {"background": handle_file(person_image_url), "layers": [], "composite": None},
        handle_file(garment_image_url),
        current_app.config["HF_TRYON_CLOTH_TYPE"],
        current_app.config["HF_TRYON_STEPS"],
        current_app.config["HF_TRYON_GUIDANCE"],
        -1,             # seed (-1 = random)
        "result only",  # show_type
        api_name=api_name,
    )

    path = _first_image_path(result)
    if not path:
        raise RuntimeError("Try-on model returned no image")
    return path


def _first_image_path(result):
    """Normalize the various shapes a Gradio Space may return into a filepath."""
    item = result
    # Galleries / multi-output endpoints return a list (possibly nested).
    while isinstance(item, (list, tuple)):
        if not item:
            return None
        item = item[0]
    if isinstance(item, dict):
        return item.get("image") or item.get("path") or item.get("name")
    return item
