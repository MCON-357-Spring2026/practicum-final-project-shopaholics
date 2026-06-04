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
# Updated to match actual DummyJSON categories
WEARABLE_CATEGORIES = ["mens-shirts", "mens-shoes", "mens-watches", "womens-dresses", "womens-shoes", "womens-watches", "womens-bags", "tops"]

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
    
    # If we have seed data, return it first
    if items:
        return items[:20]  # Limit to reasonable number
    
    # Otherwise try to get from DummyJSON
    # Note: DummyJSON doesn't have clothing-specific categories, 
    # so we'll search for clothing-related terms
    try:
        response = requests.get(
            f"{_base()}/products/search",
            params={"q": "shirt dress jacket coat sweater", "limit": 30},
            timeout=10
        )
        response.raise_for_status()
        products = response.json().get("products", [])
        
        # Filter for items that might be clothing based on title/category
        clothing_keywords = ["shirt", "dress", "jacket", "coat", "sweater", "top", "blouse", "pants", "jeans"]
        filtered = [
            p for p in products 
            if any(keyword in p.get("title", "").lower() for keyword in clothing_keywords)
        ]
        
        return filtered if filtered else products[:10]  # Return something rather than nothing
    except requests.RequestException as e:
        # If API fails, return empty list (seed data already tried above)
        current_app.logger.error(f"DummyJSON API error: {e}")
        return []


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
