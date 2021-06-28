from typing import Generator, Dict

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import pytest
from api.dependencies import get_db

from db.database import Base
from core.main import app
from tests.utils import utils as test_utils

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
