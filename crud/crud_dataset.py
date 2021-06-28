import os
from datetime import datetime
import uuid
import requests_cache

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
import petl as etl
import dateutil.parser

from models import dataset as models_dataset
from schemas import dataset as schemas_dataset
from core import settings

request_session = requests_cache.CachedSession(expire_after=settings.CACHE_TTL)


def generate_dataset_file_location(username: str):
    filename = f'{uuid.uuid4().hex}.csv'
    file_location = f'{settings.USER_DATASET_LOCATION}/{username}/{filename}'
    return file_location


def create_datasetmeta(db: Session, datasetmeta: schemas_dataset.DataSetMetaCreate):
    db_meta = models_dataset.DataSetMeta(filename=datasetmeta.filename, user_id=datasetmeta.user_id)
    db.add(db_meta)
    db.commit()
    db.refresh(db_meta)
    return db_meta


def transform_dataset(dataset: list):
    """
    Remove all unnecessary information from person data.
    Replace homeworld url with homeworld name and edited datetime with date.
    """

    def apply(person: dict):
        date_edited = person.pop('edited')
        person['date'] = dateutil.parser.parse(date_edited).date()

        all_keys = person.keys()
        to_remove = [key for key in all_keys if key not in settings.REQUIRED_DATASET_FIELDS]

        for key in to_remove:
            del person[key]

        homeworld_name = request_session.get(person['homeworld']).json()['name']

        person['homeworld'] = homeworld_name

        return person

    return map(apply, dataset)


def parse_page(start_url: str):
    """Get pages from paginated collection."""
    first_page = request_session.get(start_url).json()

    yield first_page
    next_url = first_page['next']

    while next_url:
        next_page = request_session.get(next_url).json()
        next_url = next_page['next']
        yield next_page


def create_base_user_dataset_dir(username):
    try:
        os.mkdir(f'{settings.USER_DATASET_LOCATION}/{username}')
    except FileNotFoundError:
        os.mkdir(f'{settings.USER_DATASET_LOCATION}')
        os.mkdir(f'{settings.USER_DATASET_LOCATION}/{username}')


def create_csv_file(file_location: str):
    """Create initial csv file with a header."""
    table_header = [
        settings.REQUIRED_DATASET_FIELDS
    ]

    etl.tocsv(table_header, file_location)


def fetch_dataset_to_file(file_location: str):
    """Transform information obtained from the external API and write it page by page to a csv file."""

    for counter, page in enumerate(parse_page(settings.ENTRY_DATA_ENDPOINT)):
        page = transform_dataset(page['results'])
        etl.appendcsv((row.values() for row in page), file_location, write_header=True)


def get_dataset_info_by_id(db: Session, dataset_id: int, username: str):
    data = db.query(models_dataset.DataSetMeta).filter(models_dataset.DataSetMeta.id == dataset_id).first()
    filename, owner_id = data.filename, data.user_id
    return f'{settings.USER_DATASET_LOCATION}/{username}/{filename}', owner_id


def limit_dataset(dataset, limit: int):
    return etl.head(dataset, limit)


def fetch_dataset_from_file_limited(file_location: str, load_amount: int):
    data = etl.fromcsv(source=file_location)
    return etl.head(data, load_amount)


def fetch_dataset_from_file_full(file_location: str):
    return etl.fromcsv(source=file_location)


def count_dataset_values(dataset, *values):
    return etl.valuecounts(dataset, *values)


def structurize_dataset_table(dataset):
    people = []

    for person_row in dataset.dicts():
        people.append(person_row)

    return people
