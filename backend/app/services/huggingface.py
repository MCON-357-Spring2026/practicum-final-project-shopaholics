"""
Virtual try-on via a Hugging Face Space (replaces the old Fashn.ai service).

The default Space is IDM-VTON (``yisol/IDM-VTON``). Spaces are Gradio apps, so
we call them with ``gradio_client`` rather than a raw REST endpoint. The call
is synchronous — it blocks until the model finishes — which is fine because it
runs inside the background try-on worker thread.

If the Space's API signature changes (or you switch Spaces), open its page on
huggingface.co, click "Use via API", and adjust HF_TRYON_SPACE /
HF_TRYON_API_NAME (and the predict arguments below) to match.
"""
import logging

from flask import current_app
from gradio_client import Client, handle_file

logger = logging.getLogger(__name__)


def run_tryon(
    person_image_url: str,
    garment_image_url: str,
    garment_description: str = "an item of clothing",
) -> str:
    """
    Send the person photo + garment image to the try-on Space and return a
    local filepath to the generated result image (downloaded by gradio_client).
    Raises on failure.
    """
    space = current_app.config["HF_TRYON_SPACE"]
    api_name = current_app.config["HF_TRYON_API_NAME"]
    token = current_app.config.get("HUGGINGFACE_API_TOKEN") or None

    logger.info(f"Connecting to HF Space {space}")
    client = Client(space, token=token, verbose=False)

    # Signature of IDM-VTON's /tryon (from the Space's "view API"):
    #   dict        [ImageEditor] dict(background, layers, composite)
    #   garm_img    [Image]
    #   garment_des [str]   — short text description of the garment
    #   is_checked  [bool]  — auto-generate the clothing mask
    #   is_checked_crop [bool]
    #   denoise_steps [float], seed [float]
    #   -> (output_image, masked_image)
    person = handle_file(person_image_url)
    result = client.predict(
        {"background": person, "layers": [], "composite": person},
        handle_file(garment_image_url),
        garment_description,
        True,   # is_checked — auto-generate the mask
        False,  # is_checked_crop
        current_app.config["HF_TRYON_STEPS"],
        current_app.config["HF_TRYON_SEED"],
        api_name=api_name,
    )

    # /tryon returns (output_image, masked_image); we want the first.
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
        return item.get("path") or item.get("url") or item.get("image") or item.get("name")
    return item
