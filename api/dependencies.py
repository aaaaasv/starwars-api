import requests
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from db.database import SessionLocal
from core import settings
from schemas import token as schemas_token
from crud.crud_login import oauth2_scheme
from crud.crud_user import get_user_by_username


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_availability():
    try:
        requests.get(settings.ENTRY_DATA_ENDPOINT)
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, requests.HTTPError):
        return False
    return True


async def get_current_user(db: Session = Depends(get_db), token=Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticated': 'Bearer'}
    )

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        username: str = payload.get('sub')
        if username is None:
            raise credentials_exception
        token_data = schemas_token.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def is_authenticated(db: Session = Depends(get_db), token: schemas_token.Token = Depends(oauth2_scheme)):
    try:
        user = await get_current_user(db, token)
    except HTTPException:
        return False
    if user:
        return True
