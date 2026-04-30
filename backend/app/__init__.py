from flask import Flask, jsonify

from config import get_config
from app.extensions import db, migrate, jwt, bcrypt, cors, limiter


def create_app(config_override=None) -> Flask:
    app = Flask(__name__)

    # ── Config ────────────────────────────────────────────
    app.config.from_object(get_config())
    if config_override:
        app.config.update(config_override)

    # ── Extensions ────────────────────────────────────────
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)
    cors.init_app(
        app,
        resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}},
        supports_credentials=True,
    )
    limiter.init_app(app)

    # ── Models (must be imported for Alembic autogenerate) ─
    import app.models  # noqa: F401

    # ── JWT error handlers ────────────────────────────────
    _register_jwt_callbacks(jwt)

    # ── Blueprints ────────────────────────────────────────
    _register_blueprints(app)

    # ── Shell context ─────────────────────────────────────
    @app.shell_context_processor
    def shell_context():
        return {"db": db, "app": app}

    # ── Health check ─────────────────────────────────────
    @app.get("/health")
    def health():
        return {"status": "ok"}, 200

    return app


def _register_blueprints(app: Flask) -> None:
    from app.routes.auth import auth_bp
    from app.routes.products import products_bp
    from app.routes.uploads import uploads_bp
    from app.routes.tryon import tryon_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(products_bp, url_prefix="/api/products")
    app.register_blueprint(uploads_bp, url_prefix="/api/uploads")
    app.register_blueprint(tryon_bp, url_prefix="/api/tryon")


def _register_jwt_callbacks(jwt_manager) -> None:

    @jwt_manager.expired_token_loader
    def expired_token(_jwt_header, _jwt_payload):
        return jsonify({
            "error": "token_expired",
            "message": "Token has expired"
        }), 401

    @jwt_manager.invalid_token_loader
    def invalid_token(reason):
        return jsonify({
            "error": "invalid_token",
            "message": reason
        }), 422

    @jwt_manager.unauthorized_loader
    def missing_token(reason):
        return jsonify({
            "error": "authorization_required",
            "message": reason
        }), 401

    @jwt_manager.revoked_token_loader
    def revoked_token(_jwt_header, _jwt_payload):
        return jsonify({
            "error": "token_revoked",
            "message": "Token has been revoked"
        }), 401
