import os
import sys

from dotenv import load_dotenv

# On Windows the console defaults to cp1252, which can't encode the Unicode
# characters (e.g. ✔) that libraries like gradio_client print — that crash
# would otherwise surface as a bogus "try-on failed" error. Force UTF-8.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

load_dotenv()

try:
    from app import create_app
    app = create_app()
    
    # Add debug route
    @app.route("/debug-info")
    def debug_info():
        import flask
        return {
            "status": "running",
            "python_version": sys.version,
            "flask_version": flask.__version__,
            "env": os.environ.get("FLASK_ENV", "not set")
        }, 200
        
except Exception as e:
    # Emergency fallback app
    from flask import Flask, jsonify
    import traceback
    
    app = Flask(__name__)
    error_details = traceback.format_exc()
    
    @app.route("/")
    @app.route("/health")
    @app.route("/debug-info")
    def error_info():
        return jsonify({
            "error": "Application failed to initialize",
            "message": str(e),
            "type": type(e).__name__,
            "traceback": error_details.split('\n')
        }), 500

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=os.environ.get("FLASK_ENV") == "development"
    )
