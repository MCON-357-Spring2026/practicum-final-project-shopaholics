import requests
from flask import current_app


def _headers() -> dict:
    return {
        "X-RapidAPI-Key": current_app.config["RAPIDAPI_KEY"],
        "X-RapidAPI-Host": current_app.config["RAPIDAPI_HOST"],
    }


def _base() -> str:
    return f"https://{current_app.config['RAPIDAPI_HOST']}"


def search_products(query: str, category: str = None, limit: int = 20) -> list[dict]:
    """Search products from RapidAPI. Returns a list of raw product dicts."""
    params = {"q": query, "pageSize": limit}
    if category:
        params["category"] = category

    response = requests.get(
        f"{_base()}/products/search",
        headers=_headers(),
        params=params,
        timeout=10,
    )
    response.raise_for_status()
    data = response.json()
    return data.get("results", data.get("products", []))


def get_product(external_id: str) -> dict:
    """Fetch a single product by its external ID."""
    response = requests.get(
        f"{_base()}/products/detail",
        headers=_headers(),
        params={"id": external_id},
        timeout=10,
    )
    response.raise_for_status()
    return response.json()
