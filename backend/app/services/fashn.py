import time
import requests
from flask import current_app


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {current_app.config['FASHN_API_KEY']}",
        "Content-Type": "application/json",
    }


def _base() -> str:
    return current_app.config["FASHN_API_BASE_URL"]


def submit_tryon(person_image_url: str, garment_image_url: str) -> str:
    """Submit a try-on job to Fashn.ai. Returns the prediction_id."""
    response = requests.post(
        f"{_base()}/run",
        headers=_headers(),
        json={
            "model_image": person_image_url,
            "garment_image": garment_image_url,
            "category": "tops",  # can be parameterized later
        },
        timeout=30,
    )
    response.raise_for_status()
    return response.json()["id"]


def poll_result(prediction_id: str, max_wait: int = 180, interval: int = 5) -> str:
    """
    Poll Fashn.ai until the prediction is complete.
    Returns the output image URL on success, raises on failure or timeout.
    """
    deadline = time.time() + max_wait

    while time.time() < deadline:
        response = requests.get(
            f"{_base()}/status/{prediction_id}",
            headers=_headers(),
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        status = data.get("status")

        if status == "completed":
            output = data.get("output")
            if isinstance(output, list):
                return output[0]
            return output

        if status == "failed":
            raise RuntimeError(data.get("error", "Fashn.ai prediction failed"))

        time.sleep(interval)

    raise TimeoutError(f"Fashn.ai prediction {prediction_id} timed out after {max_wait}s")
