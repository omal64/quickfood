import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
os.makedirs(INSTANCE_DIR, exist_ok=True)

DB_PATH = os.path.join(INSTANCE_DIR, "quickfood.db")


def _make_sqlite_uri(path: str) -> str:
    path = path.replace("\\", "/")
    return "sqlite:///" + path


class Config:
    # =========================
    # 🔐 SECURITY
    # =========================
    SECRET_KEY = os.environ.get("SECRET_KEY", "quickfood-dev-secret-2024")

    # =========================
    # 🗄 DATABASE
    # =========================
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", _make_sqlite_uri(DB_PATH)
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # =========================
    # 📁 UPLOADS
    # =========================
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
    MAX_CONTENT_LENGTH = 200 * 1024 * 1024  # 200 MB
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

    # =========================
    # 💳 PAYTECH (Wave, Orange Money, Visa)
    # =========================
    PAYTECH_API_KEY  = os.environ.get("PAYTECH_API_KEY",    "")
    PAYTECH_SECRET   = os.environ.get("PAYTECH_API_SECRET", "")
    PAYTECH_ENV      = os.environ.get("PAYTECH_ENV",        "test")  # "prod" en production
    PAYTECH_IPN_URL  = os.environ.get("PAYTECH_IPN_URL",    "")
    PAYTECH_SUCCESS_URL = os.environ.get("PAYTECH_SUCCESS_URL", "")
    PAYTECH_CANCEL_URL  = os.environ.get("PAYTECH_CANCEL_URL",  "")

    # =========================
    # 🍪 SESSION / LOGIN
    # =========================
    SESSION_COOKIE_SECURE    = False
    SESSION_COOKIE_HTTPONLY  = True
    SESSION_COOKIE_SAMESITE  = "Lax"
    REMEMBER_COOKIE_DURATION = timedelta(days=7)

    # =========================
    # ⚡ PERFORMANCE
    # =========================
    TEMPLATES_AUTO_RELOAD = True


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True
