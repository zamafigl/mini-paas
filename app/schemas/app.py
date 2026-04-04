from pydantic import BaseModel


class AppCreate(BaseModel):
    name: str
    image: str
    internal_port: int


class AppResponse(BaseModel):
    id: int
    name: str
    image: str
    internal_port: int
    assigned_port: int | None
    container_id: str | None
    status: str

    class Config:
        from_attributes = True