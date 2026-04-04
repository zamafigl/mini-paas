from fastapi import FastAPI
from sqlalchemy import text

from app.api.routes.apps import router as apps_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.db.models import App  # noqa: F401

app = FastAPI(title=settings.app_name)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


app.include_router(apps_router)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "app_name": settings.app_name,
    }


@app.get("/db-health")
def db_health():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return {"database": "ok"}