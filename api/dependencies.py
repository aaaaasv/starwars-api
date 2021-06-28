from db.database import SessionLocal
import requests

from core import settings


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
