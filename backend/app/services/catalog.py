"""
Product catalog backed by DummyJSON (replaces the old RapidAPI service).

DummyJSON is a free, no-signup fake-store API. Response shape for search:

    {
      "products": [
        {"id": 1, "title": "...", "brand": "...", "category": "...",
         "price": 9.99, "thumbnail": "https://...", "images": ["https://..."]},
        ...
      ],
      "total": N, "skip": 0, "limit": 30
    }
"""
import requests
from flask import current_app


def _base() -> str:
    return current_app.config["PRODUCT_API_BASE_URL"].rstrip("/")


def search_products(query: str, category: str = None, limit: int = 20) -> list[dict]:
    """Search products. Returns a list of raw product dicts."""
    response = requests.get(
        f"{_base()}/products/search",
        params={"q": query, "limit": limit},
        timeout=10,
    )
    response.raise_for_status()
    products = response.json().get("products", [])

    if category:
        products = [p for p in products if p.get("category") == category]

    return products


def get_product(external_id: str) -> dict:
    """Fetch a single product by its external ID."""
    response = requests.get(
        f"{_base()}/products/{external_id}",
        timeout=10,
    )
    response.raise_for_status()
    return response.json()
