"""
Formy — FastAPI application entry point.
"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.app.utilities import config  # validates env vars at import time
from src.app.utilities.logging_setup import configure_logging
from src.app.utilities.error_handlers import (
    http_exception_handler,
    validation_exception_handler,
    unhandled_exception_handler,
)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
PROJECT_RESOURCES_DIR = Path(config.PATH_PROJECT_RESOURCES) if config.PATH_PROJECT_RESOURCES else BASE_DIR / "resources"
PROJECT_IMAGES_DIR = PROJECT_RESOURCES_DIR / "images"


# ---------------------------------------------------------------------------
# Lifespan — startup / shutdown
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()

    # Import here to avoid circular imports; models import config
    from src.app.utilities.on_start_up import check_database
    check_database()

    yield
    # Shutdown: nothing to clean up.


# ---------------------------------------------------------------------------
# App instance
# ---------------------------------------------------------------------------
app = FastAPI(
    title=config.NAME_APP,
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# Static files
# ---------------------------------------------------------------------------
STATIC_DIR.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
PROJECT_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
app.mount(
    "/resource-images",
    StaticFiles(directory=str(PROJECT_IMAGES_DIR)),
    name="resource-images",
)

# ---------------------------------------------------------------------------
# Templates (shared instance imported by routes)
# ---------------------------------------------------------------------------
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# ---------------------------------------------------------------------------
# Exception handlers
# ---------------------------------------------------------------------------
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

# ---------------------------------------------------------------------------
# Routers (registered after models are importable)
# ---------------------------------------------------------------------------
from src.app.routes import auth as auth_router          # noqa: E402
from src.app.routes import admin as admin_router        # noqa: E402
from src.app.routes import questionnaire as q_router    # noqa: E402

app.include_router(auth_router.router)
app.include_router(admin_router.router)
app.include_router(q_router.router)
