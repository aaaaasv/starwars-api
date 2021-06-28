from sqlalchemy.orm import Session

from crud import crud_user
from schemas import user as schemas_user
from models import user as models_user


def test_create_user(db: Session):
    user_in = schemas_user.UserCreate(username='username1', password='12345')
    user = crud_user.create_user(db, user_in)
    assert user.username == user_in.username
    assert hasattr(user, 'password')


def test_get_user(db: Session):
    user_in = schemas_user.UserCreate(username='testusername', password='testpassword')
    db_user = crud_user.create_user(db, user_in)

    assert db.query(models_user.User).filter(models_user.User.username == user_in.username).first()
    assert crud_user.get_user(db, db_user.id)


def test_get_user_by_username(db: Session):
    user_in = schemas_user.UserCreate(username='testusername2', password='testpassword2')
    db_user = crud_user.create_user(db, user_in)

    assert db.query(models_user.User).filter(models_user.User.username == user_in.username).first()
    assert crud_user.get_user_by_username(db, db_user.username)
