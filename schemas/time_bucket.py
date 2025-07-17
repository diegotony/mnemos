from pydantic import BaseModel

class TimeBucketBase(BaseModel):
    name: str
    slug: str

class TimeBucketCreate(TimeBucketBase):
    pass

class TimeBucketRead(TimeBucketBase):
    id: int

    class Config:
        from_attributes = True  # Para usar con ORM
