from fastapi import FastAPI

from api.api_v1.api import api_router
from db.database import engine
from models import dataset, user

from core import settings

dataset.Base.metadata.create_all(bind=engine)
user.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(api_router, prefix=settings.API_V1_STR)
