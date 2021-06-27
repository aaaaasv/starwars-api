from fastapi import FastAPI

from api.api_v1.api import api_router
from db.database import engine
from models import dataset, user

dataset.Base.metadata.create_all(bind=engine)
user.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(api_router, prefix='/api/v1')
