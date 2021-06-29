from typing import Generator, Dict

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import requests
import pytest

from api.dependencies import get_db
from db.database import Base
from core.main import app
from tests.utils import utils as test_utils
from crud import crud_dataset

TEST_DATASETS_DIR = 'tests/test_datasets'

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="session", autouse=False)
def db() -> Generator:
    session = TestingSessionLocal()
    yield session

    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="module")
def client(db) -> TestClient:
    def _get_db_override():
        return db

    app.dependency_overrides[get_db] = _get_db_override
    return TestClient(app)


@pytest.fixture(scope="module")
def user_token_headers(client: TestClient, db: Session) -> Dict[str, str]:
    return test_utils.get_authentication_token(
        client=client, username='maintestuser', db=db
    )


@pytest.fixture()
def mocked_user_dataset_dir(mocker):
    mocker.patch.object(crud_dataset.settings, 'USER_DATASET_LOCATION', TEST_DATASETS_DIR)


@pytest.fixture()
def mocked_homeworld_url(mocker):
    homeworld_response = requests.Response()
    homeworld_response._content = b'{"name" : "testhomeworld"}'
    mocker.patch('crud.crud_dataset.request_session.get', return_value=homeworld_response)
