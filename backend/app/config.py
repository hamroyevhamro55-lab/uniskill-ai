import os


def _db_url() -> str:
    url = os.getenv("DATABASE_URL", "sqlite:///./uniskill.db")
    # Render/Heroku "postgres://" -> SQLAlchemy + psycopg3
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+psycopg://", 1)
    elif url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


DATABASE_URL = _db_url()
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me-this-is-not-for-production-use")
TOKEN_HOURS = int(os.getenv("TOKEN_HOURS", "72"))
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",") if o.strip()]
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
AI_MODEL = os.getenv("AI_MODEL", "claude-sonnet-5-5")
SEED_DEMO = os.getenv("SEED_DEMO", "1") == "1"
# Universitet (ekspert) akkaunti shu orqali yaratiladi; ochiq ro'yxatdan o'tishda bu rol yo'q.
UNIVERSITY_EMAIL = os.getenv("UNIVERSITY_EMAIL", "")
UNIVERSITY_PASSWORD = os.getenv("UNIVERSITY_PASSWORD", "")
