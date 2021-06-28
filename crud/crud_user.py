from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from core import settings
from models import user as models_user
from schemas import token as schemas_token
from schemas import user as schemas_user
from api.dependencies import get_db
from crud.crud_login import oauth2_scheme, get_password_hash


def get_user(db: Session, user_id: int):
    return db.query(models_user.User).filter(models_user.User.id == user_id).first()


def get_user_by_username(db: Session, username: str):
    return db.query(models_user.User).filter(models_user.User.username == username).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models_user.User).offset(skip).limit(limit).all()


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


def create_user(db: Session, user: schemas_user.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models_user.User(username=user.username, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
