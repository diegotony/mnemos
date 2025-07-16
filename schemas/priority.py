from pydantic import BaseModel

class PriorityBase(BaseModel):
    name: str

class PriorityCreate(PriorityBase):
    pass

class PriorityRead(PriorityBase):
    id: int

    class Config:
        from_attributes = True
