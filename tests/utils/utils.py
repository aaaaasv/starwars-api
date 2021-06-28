from typing import Dict

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from crud import crud_user
from schemas import user as schemas_user
from core import settings


def get_authentication_token(client: TestClient, username: str, db: Session) -> Dict[str, str]:
    """
    Return a valid token for the user with given email.

    If the user doesn't exist it is created first.
    """
    password = 'testpassword'
    user = crud_user.get_user_by_username(db, username=username)
    if not user:
        user_in_create = schemas_user.UserCreate(username=username, password=password)
        crud_user.create_user(db, user=user_in_create)
    data = {'username': username, 'password': password}
    response = client.post(f'{settings.API_V1_STR}/users/token', data=data)

    auth_token = response.json()['access_token']
    return {'Authorization': f'Bearer {auth_token}'}
