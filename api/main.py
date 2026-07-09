"""FastAPI application entry point."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from api.dependencies import get_app_settings
from api.routes import router
from utils.logging import configure_logging


def create_app() -> FastAPI:
    """Build the FastAPI application instance."""

    settings = get_app_settings()
    configure_logging(settings.logs_dir)

    app = FastAPI(title=settings.app_name, version="1.0.0")
    app.include_router(router)
    app.mount("/static", StaticFiles(directory=str(settings.frontend_dir)), name="static")

    @app.get("/")
    def root() -> FileResponse:
        return FileResponse(settings.frontend_dir / "index.html")

    @app.get("/favicon.ico")
    def favicon() -> FileResponse:
        return FileResponse(settings.frontend_dir / "favicon.ico")

    return app


app = create_app()
