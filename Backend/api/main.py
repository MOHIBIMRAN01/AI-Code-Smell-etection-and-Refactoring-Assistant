from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.dependencies import get_app_settings
from api.routes import router
from utils.logging import configure_logging
from config.database import Base, engine, migrate_database
from services.cleanup_service import RepoCloneCleanupService

def create_app() -> FastAPI:
    """Build the FastAPI application instance."""
    settings = get_app_settings()
    configure_logging(settings.logs_dir)

    # Initialize database tables and apply lightweight schema migrations.
    Base.metadata.create_all(bind=engine)
    migrate_database()

    cleanup_service = RepoCloneCleanupService(settings)

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        cleanup_service.start()
        yield
        cleanup_service.stop()

    app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)

    # Add CORS middleware to support frontend API connections
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router)

    @app.get("/")
    def root() -> dict[str, str]:
        return {"message": "Welcome to CodeSmell AI Backend REST API"}

    return app

app = create_app()
