from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.db.models.app import App
from app.schemas.app import AppCreate, AppResponse
from app.services.docker_service import DockerService
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

@router.get("/{app_id}/logs")
def get_app_logs(app_id: int, db: Session = Depends(get_db)):
    app = db.query(App).filter(App.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="App not found")

    if not app.container_id:
        raise HTTPException(status_code=400, detail="App is not deployed")

    docker_service = DockerService()

    try:
        logs = docker_service.get_logs(app.container_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get logs: {str(e)}")

    return {"logs": logs}
@router.post("/{app_id}/deploy", response_model=AppResponse)

def deploy_app(app_id: int, db: Session = Depends(get_db)):
    app = db.query(App).filter(App.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="App not found")

    if app.container_id:
        raise HTTPException(status_code=400, detail="App is already deployed")

    docker_service = DockerService()
    assigned_port = docker_service.get_free_port()

    safe_container_name = f"mini-paas-app-{app.id}"

    try:
        container = docker_service.run_container(
            name=safe_container_name,
            image=app.image,
            internal_port=app.internal_port,
            external_port=assigned_port,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Deploy failed: {str(e)}")

    app.assigned_port = assigned_port
    app.container_id = container.id
    app.status = "running"

    db.commit()
    db.refresh(app)

    return app

@router.post("/{app_id}/stop", response_model=AppResponse)
def stop_app(app_id: int, db: Session = Depends(get_db)):
    app = db.query(App).filter(App.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="App not found")

    if not app.container_id:
        raise HTTPException(status_code=400, detail="App is not deployed")

    docker_service = DockerService()

    try:
        docker_service.stop_container(app.container_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stop failed: {str(e)}")

    app.status = "stopped"
    db.commit()
    db.refresh(app)

    return app

@router.post("/{app_id}/remove", response_model=AppResponse)
def remove_app_container(app_id: int, db: Session = Depends(get_db)):
    app = db.query(App).filter(App.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="App not found")

    if not app.container_id:
        raise HTTPException(status_code=400, detail="App is not deployed")

    docker_service = DockerService()

    try:
        docker_service.remove_container(app.container_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Remove failed: {str(e)}")

    app.container_id = None
    app.assigned_port = None
    app.status = "created"
    db.commit()
    db.refresh(app)

    return app