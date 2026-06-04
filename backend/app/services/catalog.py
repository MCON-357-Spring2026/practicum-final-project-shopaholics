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
import json
import os

import requests
from flask import current_app

# DummyJSON categories that are actual wearable garments (what try-on supports).
WEARABLE_CATEGORIES = ["mens-shirts", "tops", "womens-dresses"]

# Local seed catalog of extra garments (free, reliable images from the
# IDM-VTON Space's example set — known to work well with the try-on model).
_SEED_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "seed_products.json")


def _base() -> str:
    return current_app.config["PRODUCT_API_BASE_URL"].rstrip("/")


def load_seed() -> list[dict]:
    """Load the bundled seed garments (returns [] if the file is missing/bad)."""
    try:
        with open(_SEED_PATH, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return []


def list_wearables() -> list[dict]:
    """Return all garments from the wearable categories (for default browsing).

    Combines the bundled seed catalog with live DummyJSON results so the page
    is never empty even if the external API is unreachable.
    """
    items: list[dict] = list(load_seed())
    for slug in WEARABLE_CATEGORIES:
        try:
            response = requests.get(f"{_base()}/products/category/{slug}", timeout=10)
            response.raise_for_status()
            items.extend(response.json().get("products", []))
        except requests.RequestException:
            continue  # skip a failing category rather than break the whole page
    return items


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
