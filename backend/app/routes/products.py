from datetime import datetime, timezone

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required

from app.extensions import db
from app.models.product import Product
from app.services import catalog
from app.repositories import ProductRepository

products_bp = Blueprint("products", __name__)


def _is_cache_fresh(product: Product) -> bool:
    ttl = current_app.config["PRODUCT_CACHE_TTL_SECONDS"]
    age = (datetime.now(timezone.utc) - product.cached_at).total_seconds()
    return age < ttl


def _upsert_product(raw: dict) -> Product:
    """Persist or refresh a product from a raw DummyJSON dict."""
    external_id = str(raw.get("id"))
    product_repo = ProductRepository()
    
    images = raw.get("images") or []
    product_data = {
        "title": raw.get("title"),
        "brand": raw.get("brand") or raw.get("category"),
        "image_url": raw.get("thumbnail") or (images[0] if images else None),
        "category": raw.get("category"),
        "price": raw.get("price"),
        "raw_data": raw
    }
    
    product = product_repo.get_by_external_id(int(external_id))
    if product:
        product = product_repo.update_from_external(product, **product_data)
    else:
        product = product_repo.get_or_create(int(external_id), **product_data)
    
    return product


# ── Featured / browse ────────────────────────────────────
@products_bp.get("/featured")
@jwt_required()
def featured():
    """Return all wearable garments so the catalog has items without searching."""
    try:
        raw_results = catalog.list_wearables()
    except Exception as e:
        current_app.logger.error(f"Catalog API error: {e}")
        return jsonify({"error": "Failed to fetch products"}), 502

    products = [_upsert_product(r) for r in raw_results]
    return jsonify([p.to_dict() for p in products]), 200


# ── Search ───────────────────────────────────────────────
@products_bp.get("/search")
@jwt_required()
def search():
    query = request.args.get("q", "").strip()
    category = request.args.get("category")
    limit = min(int(request.args.get("limit", 20)), 50)

    if not query:
        return jsonify({"error": "Query parameter 'q' is required"}), 400

    try:
        raw_results = catalog.search_products(query, category=category, limit=limit)
    except Exception as e:
        current_app.logger.error(f"RapidAPI error: {e}")
        return jsonify({"error": "Failed to fetch products"}), 502

    products = [_upsert_product(r) for r in raw_results]
    return jsonify([p.to_dict() for p in products]), 200


# ── Single product ────────────────────────────────────────
@products_bp.get("/<string:product_id>")
@jwt_required()
def get_product(product_id: str):
    product_repo = ProductRepository()
    product = product_repo.get_by_id(product_id)

    if not product:
        return jsonify({"error": "Product not found"}), 404

    if not _is_cache_fresh(product):
        try:
            raw = catalog.get_product(product.external_id)
            product = _upsert_product(raw)
        except Exception as e:
            current_app.logger.warning(f"Cache refresh failed: {e}")

    return jsonify(product.to_dict()), 200
