import os
from datetime import datetime
import uuid
import requests

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
import petl as etl
import dateutil.parser

from models import dataset as models_dataset
from schemas import dataset as schemas_dataset
from core import settings


def generate_dataset_metadata(username: str):
    filename = f'{uuid.uuid4().hex}.csv'
    file_location = f'{settings.USER_DATASET_LOCATION}/{username}/{filename}'
    return datetime.now(), file_location


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
        del person['url'], person['created'], person['vehicles'], person['films'], person['starships'], person[
            'species']

        homeworld_name = requests.get(person['homeworld']).json()['name']

        date_edited = person.pop('edited')
        person['date'] = dateutil.parser.parse(date_edited).date()
        person['homeworld'] = homeworld_name

        return person

    return map(apply, dataset)


def parse_page(start_url: str):
    """Get pages from paginated collection."""
    request_session = requests.Session()

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
        ['name', 'height', 'mass', 'hair_color', 'skin_color', 'eye_color', 'birth_year', 'gender', 'homeworld', 'date']
    ]

    etl.tocsv(table_header, file_location)


def fetch_dataset_to_file(file_location: str):
    """Transform information obtained from the external API and write it page by page to a csv file."""
    for counter, page in enumerate(parse_page(settings.ENTRY_DATA_ENDPOINT)):
        page = list(transform_dataset(page['results']))
        etl.appendcsv((row.values() for row in page), file_location, write_header=True)


def get_dataset_filename_by_id(db: Session, dataset_id: int):
    try:
        return db.query(models_dataset.DataSetMeta).filter(models_dataset.DataSetMeta.id == dataset_id).first().filename
    except AttributeError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND
        )


def fetch_dataset_from_file_limited(file_location: str, load_amount: int):
    data = etl.fromcsv(source=file_location)
    return etl.head(data, load_amount)


def fetch_dataset_from_file_full(file_location: str):
    row_number = etl.nrows(etl.fromcsv(source=file_location))
    return fetch_dataset_from_file_limited(file_location, row_number)
