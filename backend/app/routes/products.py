from datetime import datetime, timezone

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required

from app.extensions import db
from app.models.product import Product
from app.services import catalog

products_bp = Blueprint("products", __name__)


def _is_cache_fresh(product: Product) -> bool:
    ttl = current_app.config["PRODUCT_CACHE_TTL_SECONDS"]
    age = (datetime.now(timezone.utc) - product.cached_at).total_seconds()
    return age < ttl


def _upsert_product(raw: dict) -> Product:
    """Persist or refresh a product from a raw DummyJSON dict."""
    external_id = str(raw.get("id"))

    product = Product.query.filter_by(external_id=external_id).first()

    if not product:
        product = Product(external_id=external_id)
        db.session.add(product)

    images = raw.get("images") or []
    product.title = raw.get("title")
    # DummyJSON omits "brand" on some items — fall back to the category.
    product.brand = raw.get("brand") or raw.get("category")
    product.image_url = raw.get("thumbnail") or (images[0] if images else None)
    product.category = raw.get("category")
    product.price = raw.get("price")
    product.raw_data = raw
    product.cached_at = datetime.now(timezone.utc)

    db.session.commit()
    return product


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
    product = db.session.get(Product, product_id)

    if not product:
        return jsonify({"error": "Product not found"}), 404

    if not _is_cache_fresh(product):
        try:
            raw = catalog.get_product(product.external_id)
            product = _upsert_product(raw)
        except Exception as e:
            current_app.logger.warning(f"Cache refresh failed: {e}")

    return jsonify(product.to_dict()), 200
