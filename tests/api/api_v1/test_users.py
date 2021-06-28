from typing import Dict

from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from schemas import user as schemas_user
from core import settings
from crud import crud_user


def test_create_user(client: TestClient, db: Session):
    username = 'createdusername'
    password = 'testpassword'
    data = {'username': username, 'password': password}
    response = client.post(f'{settings.API_V1_STR}/users/', json=data)
    assert 200 <= response.status_code < 300
    created_user = response.json()
    user = crud_user.get_user_by_username(db, username)
    assert user
    assert user.username == created_user['username']


def test_get_user_datasets_success(client: TestClient, db: Session, user_token_headers: Dict[str, str]):
    response = client.get(f'{settings.API_V1_STR}/users/me', headers=user_token_headers)

    assert response.status_code == 200
    assert 'datasetmeta' in response.json()


def test_get_user_datasets_fail_not_auth(client: TestClient, db: Session):
    response = client.get(f'{settings.API_V1_STR}/users/me')

    assert response.status_code == 401


def test_retrieve_token(client: TestClient, db: Session):
    username = 'tokenusername'
    password = 'testpassword'
    data = {'username': username, 'password': password}

    user = crud_user.create_user(db, schemas_user.UserCreate(**data))

    assert user

    response = client.post(f'{settings.API_V1_STR}/users/token', data=data)
    assert 'access_token' in response.json()
    assert 'token_type' in response.json()

    access_token = response.json()['access_token']

    response = client.get(f'{settings.API_V1_STR}/users/me',
                          headers={'Authorization': f'Bearer {access_token}'})

    assert response.status_code == 200
