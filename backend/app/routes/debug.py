from flask import Blueprint, jsonify
import os
from app.services import catalog

debug_bp = Blueprint("debug", __name__)

@debug_bp.get("/debug/seed")
def debug_seed():
    """Debug endpoint to check seed data loading."""
    try:
        # Check if seed file exists
        seed_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "seed_products.json")
        exists = os.path.exists(seed_path)
        
        # Try to load seed data
        seed_data = catalog.load_seed()
        
        # Try to get wearables
        wearables = catalog.list_wearables()
        
        return jsonify({
            "seed_path": seed_path,
            "seed_exists": exists,
            "seed_count": len(seed_data),
            "wearables_count": len(wearables),
            "first_seed": seed_data[0] if seed_data else None,
            "first_wearable": wearables[0] if wearables else None,
            "cwd": os.getcwd(),
            "dirname": os.path.dirname(__file__)
        }), 200
    except Exception as e:
        import traceback
        return jsonify({
            "error": str(e),
            "type": type(e).__name__,
            "traceback": traceback.format_exc().split('\n')
        }), 500