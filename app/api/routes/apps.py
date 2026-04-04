from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.db.models.app import App
from app.schemas.app import AppCreate, AppResponse

router = APIRouter(prefix="/apps", tags=["apps"])


@router.post("", response_model=AppResponse)
def create_app(payload: AppCreate, db: Session = Depends(get_db)):
    existing_app = db.query(App).filter(App.name == payload.name).first()
    if existing_app:
        raise HTTPException(status_code=400, detail="App with this name already exists")

    app = App(
        name=payload.name,
        image=payload.image,
        internal_port=payload.internal_port,
        status="created",
    )
    db.add(app)
    db.commit()
    db.refresh(app)
    return app


@router.get("", response_model=list[AppResponse])
def list_apps(db: Session = Depends(get_db)):
    return db.query(App).all()


@router.get("/{app_id}", response_model=AppResponse)
def get_app(app_id: int, db: Session = Depends(get_db)):
    app = db.query(App).filter(App.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="App not found")
    return app