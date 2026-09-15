import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")


class Config:
    AZURE_CLIENT_ID = os.environ.get("AZURE_CLIENT_ID")
    AZURE_TENANT_ID = os.environ.get("AZURE_TENANT_ID")
    SENDER_EMAIL = os.environ.get("SENDER_EMAIL")

    MIN_DELAY_SECONDS = int(os.environ.get("MIN_DELAY_SECONDS", 45))
    MAX_DELAY_SECONDS = int(os.environ.get("MAX_DELAY_SECONDS", 180))
    MAX_EMAILS_PER_DAY = int(os.environ.get("MAX_EMAILS_PER_DAY", 40))
    FOLLOWUP_1_DAYS = int(os.environ.get("FOLLOWUP_1_DAYS", 1))
    FOLLOWUP_2_DAYS = int(os.environ.get("FOLLOWUP_2_DAYS", 3))
    WORKER_INTERVAL_SECONDS = int(os.environ.get("WORKER_INTERVAL_SECONDS", 300))

    PUBLIC_BASE_URL = os.environ.get("PUBLIC_BASE_URL", "").strip().rstrip("/")

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(INSTANCE_DIR, 'outreach.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    TOKEN_CACHE_PATH = os.environ.get(
        "TOKEN_CACHE_PATH", os.path.join(INSTANCE_DIR, "token_cache.bin")
    )

    @classmethod
    def tracking_enabled(cls) -> bool:
        return bool(cls.PUBLIC_BASE_URL)
