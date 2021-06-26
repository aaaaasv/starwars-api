from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

import settings
from api.dependencies import get_db
from crud import crud_user, crud_login
from schemas import user as schemas_user
from schemas import token as schemas_token

router = APIRouter()


@router.post('/', response_model=schemas_user.User)
def create_user(user: schemas_user.UserCreate, db: Session = Depends(get_db)):
    db_user = crud_user.get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(
            detail='Username already registered',
            status_code=status.HTTP_400_BAD_REQUEST
        )

    return crud_user.create_user(db, user)


@router.post('/token', response_model=schemas_token.Token)
async def get_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = crud_login.authenticate(db, username=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'}
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = crud_login.create_access_token(
        data={'sub': user.username}, expires_delta=access_token_expires
    )
    return {'access_token': access_token, 'token_type': 'bearer'}


@router.get('/is_authenticated')
async def is_user_authenticated(is_authenticated: bool = Depends(crud_user.is_authenticated)):
    if is_authenticated:
        return {'detail': 'Authenticated'}
    else:
        return {'detail': 'Not authenticated'}


@router.get('/me', response_model=schemas_user.User)
def get_current_user(current_user: schemas_user.User = Depends(crud_user.get_current_user)):
    return current_user
