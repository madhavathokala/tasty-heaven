import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """
    Central configuration for the Flask application.

    SECRET_KEY is used by Flask to sign the session cookie. In production
    this MUST be set via an environment variable. For local development a
    fallback value is provided so the app can run out of the box.
    """

    SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "tasty-heaven-local-dev-key-change-this"
) 

    # SQLite database stored inside the instance/ folder.
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///" + os.path.join(BASE_DIR, "instance", "tasty_heaven.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Session / cookie configuration
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # JSON should keep key order & not escape special characters (for ₹ symbol etc.)
    JSON_AS_ASCII = False
