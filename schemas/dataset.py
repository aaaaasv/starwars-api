import datetime
from pydantic import BaseModel


class DataSetMeta(BaseModel):
    id: int
    filename: str
    created_at: datetime.datetime
    user_id: int

    class Config:
        orm_mode = True


class DataSetMetaCreate(BaseModel):
    filename: str
    created_at: datetime.datetime
    user_id: int
