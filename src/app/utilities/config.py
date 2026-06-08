"""
Application configuration — loads and validates environment variables at startup.
Missing required variables trigger a fatal error (sys.exit with non-zero code).
"""

from __future__ import annotations

import os
import sys
from dotenv import load_dotenv

load_dotenv()

VALID_ENVIRONMENTS = {"development", "testing", "production"}


def _require(var: str) -> str:
    """Return the value of an env var or exit fatally if missing/empty."""
    value = os.getenv(var, "").strip()
    if not value:
        print(f"FATAL: Required environment variable '{var}' is missing or empty.", file=sys.stderr)
        sys.exit(1)
    return value


def _require_for_env(var: str, current_env: str, required_in: set[str]) -> str | None:
    """Return the value of an env var, or exit fatally if required in the current environment."""
    value = os.getenv(var, "").strip()
    if current_env in required_in and not value:
        print(
            f"FATAL: Environment variable '{var}' is required in '{current_env}' but is missing or empty.",
            file=sys.stderr,
        )
        sys.exit(1)
    return value or None


# ---------------------------------------------------------------------------
# Required in all environments
# ---------------------------------------------------------------------------
NAME_APP: str = _require("NAME_APP")

RUN_ENVIRONMENT: str = _require("RUN_ENVIRONMENT")
if RUN_ENVIRONMENT not in VALID_ENVIRONMENTS:
    print(
        f"FATAL: RUN_ENVIRONMENT='{RUN_ENVIRONMENT}' is invalid. "
        f"Must be one of: {', '.join(sorted(VALID_ENVIRONMENTS))}",
        file=sys.stderr,
    )
    sys.exit(1)

SECRET_KEY: str = _require("SECRET_KEY")
URL_BASE_WEBSITE: str = _require("URL_BASE_WEBSITE")
EMAIL_ADMIN_USER: str = _require("EMAIL_ADMIN_USER")

# Comma-separated → set of allowed emails (stripped, lowercased)
ALLOWED_ADMIN_EMAILS: set[str] = {
    e.strip().lower() for e in EMAIL_ADMIN_USER.split(",") if e.strip()
}

# ---------------------------------------------------------------------------
# Optional / environment-specific
# ---------------------------------------------------------------------------
PATH_PROJECT_RESOURCES: str | None = os.getenv("PATH_PROJECT_RESOURCES", "").strip() or None
AUDIO_FILES_PATH: str | None = os.getenv("AUDIO_FILES_PATH", "").strip() or None
HERO_IMAGE_FILENAME: str = os.getenv("HERO_IMAGE_FILENAME", "hello_picture.jpg").strip() or "hello_picture.jpg"

# Database — PostgreSQL
DB_HOST: str = _require("DB_HOST")
DB_PORT: str = _require("DB_PORT")
DB_NAME: str = _require("DB_NAME")
DB_USER: str = _require("DB_USER")
DB_SCHEMA: str | None = os.getenv("DB_SCHEMA", "").strip() or None

GMAIL_SMTP_USER: str | None = os.getenv("GMAIL_SMTP_USER", "").strip() or None
GMAIL_SMTP_APP_PASSWORD: str | None = os.getenv("GMAIL_SMTP_APP_PASSWORD", "").strip() or None
GMAIL_SMTP_HOST: str = os.getenv("GMAIL_SMTP_HOST", "smtp.gmail.com").strip()
GMAIL_SMTP_PORT: int = int(os.getenv("GMAIL_SMTP_PORT", "587"))

# ---------------------------------------------------------------------------
# Logging — PATH_TO_LOGS is required in testing and production
# ---------------------------------------------------------------------------
PATH_TO_LOGS: str | None = _require_for_env(
    "PATH_TO_LOGS", RUN_ENVIRONMENT, {"testing", "production"}
)

_log_max_size_raw = os.getenv("LOG_MAX_SIZE_IN_MB", "5").strip()
LOG_MAX_SIZE_IN_MB: int = int(_log_max_size_raw) if _log_max_size_raw.isdigit() else 5

_log_max_files_raw = os.getenv("LOG_MAX_FILES", "5").strip()
LOG_MAX_FILES: int = int(_log_max_files_raw) if _log_max_files_raw.isdigit() else 5

# ---------------------------------------------------------------------------
# Derived helpers
# ---------------------------------------------------------------------------
DEBUG: bool = RUN_ENVIRONMENT == "development"
