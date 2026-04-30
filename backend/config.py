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

    # ── AWS S3 ────────────────────────────────────────────────────────────
    AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
    AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
    S3_BUCKET = os.environ.get("S3_BUCKET")
    S3_PRESIGNED_URL_EXPIRY = int(os.environ.get("S3_PRESIGNED_URL_EXPIRY", 900))  # 15 min

    # ── External APIs ─────────────────────────────────────────────────────
    RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY")
    RAPIDAPI_HOST = os.environ.get("RAPIDAPI_HOST", "apidojo-h-and-m-hm-v1.p.rapidapi.com")
    FASHN_API_KEY = os.environ.get("FASHN_API_KEY")
    FASHN_API_BASE_URL = os.environ.get("FASHN_API_BASE_URL", "https://api.fashn.ai/v1")

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
