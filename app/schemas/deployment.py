from datetime import datetime

from pydantic import BaseModel


class DeploymentResponse(BaseModel):
    id: int
    app_id: int
    status: str
    started_at: datetime
    finished_at: datetime | None
    error_message: str | None

    class Config:
        from_attributes = True
