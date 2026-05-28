import os
from datetime import timedelta


class Config:
    # ── Core ──────────────────────────────────────────────────────────────
    SECRET_KEY = os.environ["SECRET_KEY"]
    DEBUG = False
    TESTING = False

    # ── Database ──────────────────────────────────────────────────────────
    # Render provides DATABASE_URL with the "postgres://" scheme; SQLAlchemy
    # 1.4+ requires "postgresql://".  Fix it transparently here.
    _raw_db_url = os.environ.get("DATABASE_URL", "")
    SQLALCHEMY_DATABASE_URI = (
        _raw_db_url.replace("postgres://", "postgresql://", 1)
        if _raw_db_url.startswith("postgres://")
        else _raw_db_url
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,      # drop stale connections before use
        "pool_recycle": 300,        # recycle connections every 5 min
    }

    # ── JWT ───────────────────────────────────────────────────────────────
    JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"]
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_TOKEN_LOCATION = ["headers"]
    JWT_HEADER_NAME = "Authorization"
    JWT_HEADER_TYPE = "Bearer"

    # ── CORS ──────────────────────────────────────────────────────────────
    # Comma-separated list: FRONTEND_URL=https://fitvision.onrender.com
    CORS_ORIGINS = [
        o.strip()
        for o in os.environ.get("FRONTEND_URL", "http://localhost:5173").split(",")
    ]

    # ── Cloudinary (image storage — replaces AWS S3) ──────────────────────
    CLOUDINARY_CLOUD_NAME = os.environ.get("CLOUDINARY_CLOUD_NAME")
    CLOUDINARY_API_KEY = os.environ.get("CLOUDINARY_API_KEY")
    CLOUDINARY_API_SECRET = os.environ.get("CLOUDINARY_API_SECRET")

    # ── Product catalog API (DummyJSON — no key needed) ───────────────────
    PRODUCT_API_BASE_URL = os.environ.get("PRODUCT_API_BASE_URL", "https://dummyjson.com")

    # ── Hugging Face try-on (replaces Fashn.ai) ───────────────────────────
    # Default model is the CatVTON Space. The Space's exact API can be found
    # on its page under "Use via API"; override these if it changes.
    HUGGINGFACE_API_TOKEN = os.environ.get("HUGGINGFACE_API_TOKEN")
    HF_TRYON_SPACE = os.environ.get("HF_TRYON_SPACE", "zhengchong/CatVTON")
    HF_TRYON_API_NAME = os.environ.get("HF_TRYON_API_NAME", "/submit_function")
    HF_TRYON_STEPS = int(os.environ.get("HF_TRYON_STEPS", 50))
    HF_TRYON_GUIDANCE = float(os.environ.get("HF_TRYON_GUIDANCE", 2.5))
    HF_TRYON_CLOTH_TYPE = os.environ.get("HF_TRYON_CLOTH_TYPE", "upper")

    # ── Product cache ─────────────────────────────────────────────────────
    PRODUCT_CACHE_TTL_SECONDS = int(os.environ.get("PRODUCT_CACHE_TTL_SECONDS", 3600))

    # ── Rate limiting ─────────────────────────────────────────────────────
    RATELIMIT_STORAGE_URL = os.environ.get("RATELIMIT_STORAGE_URL", "memory://")
    RATELIMIT_DEFAULT = "200 per day;50 per hour"


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/fitvision_dev",
    )
    # Relaxed limits in dev so manual testing is easy
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)


class ProductionConfig(Config):
    # Render sets PORT automatically; Gunicorn reads it from the start command.
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "pool_size": 5,
        "max_overflow": 10,
    }


class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)
    # Disable CSRF / rate limiting in tests
    WTF_CSRF_ENABLED = False


config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}


def get_config() -> Config:
    env = os.environ.get("FLASK_ENV", "development")
    return config_map.get(env, DevelopmentConfig)
