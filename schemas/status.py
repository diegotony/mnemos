from pydantic import BaseModel

class StatusBase(BaseModel):
    name: str

class StatusCreate(StatusBase):
    pass

class StatusRead(StatusBase):
    id: int

    class Config:
        orm_mode = True
