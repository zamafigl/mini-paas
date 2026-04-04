from fastapi import FastAPI
from app.core.config import settings

app = FastAPI(title=settings.app_name)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "app_name": settings.app_name,
    }