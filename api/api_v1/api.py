from fastapi import APIRouter

from .endpoints import datasets, users

api_router = APIRouter()
api_router.include_router(datasets.router, prefix='/datasets', tags=['datasets'])
api_router.include_router(users.router, prefix='/users', tags=['users'])
