from datetime import datetime

from sqlalchemy.orm import Session

from app.db.models.app import App
from app.db.models.deployment import Deployment
from app.db.session import SessionLocal
from app.services.docker_service import DockerService


def deploy_app_job(app_id: int) -> None:
    db: Session = SessionLocal()
    deployment = None
    app = None

    try:
        app = db.query(App).filter(App.id == app_id).first()
        if not app:
            return

        deployment = Deployment(
            app_id=app.id,
            status="running",
            started_at=datetime.utcnow(),
        )
        db.add(deployment)
        db.commit()
        db.refresh(deployment)

        if app.container_id:
            deployment.status = "failed"
            deployment.finished_at = datetime.utcnow()
            deployment.error_message = "App is already deployed"
            db.commit()
            return

        docker_service = DockerService()
        assigned_port = docker_service.get_free_port()
        safe_container_name = f"mini-paas-app-{app.id}"

        container = docker_service.run_container(
            name=safe_container_name,
            image=app.image,
            internal_port=app.internal_port,
            external_port=assigned_port,
        )

        app.assigned_port = assigned_port
        app.container_id = container.id
        app.status = "running"

        deployment.status = "success"
        deployment.finished_at = datetime.utcnow()

        db.commit()
        db.refresh(app)

    except Exception as e:
        if deployment:
            deployment.status = "failed"
            deployment.finished_at = datetime.utcnow()
            deployment.error_message = str(e)

        if app:
            app.status = "failed"

        db.commit()
        raise

    finally:
        db.close()
