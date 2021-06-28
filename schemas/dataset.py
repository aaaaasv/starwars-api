from typing import List, Optional
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
    user_id: int


class DataSet(BaseModel):
    name: str
    height: str
    mass: str
    hair_color: str
    skin_color: str
    eye_color: str
    birth_year: str
    gender: str
    homeworld: str
    date: datetime.date


class DataSetCollection(BaseModel):
    datasets: List[DataSet]


class DataSetCounted(BaseModel):
    name: Optional[str]
    height: Optional[str]
    mass: Optional[str]
    hair_color: Optional[str]
    skin_color: Optional[str]
    eye_color: Optional[str]
    birth_year: Optional[str]
    gender: Optional[str]
    homeworld: Optional[str]
    date: Optional[datetime.date]
    count: int


class DataSetCountedCollection(BaseModel):
    datasets: List[DataSetCounted]
