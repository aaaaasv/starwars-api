from sqlalchemy.orm import Session
import datetime
import requests
import json

from crud import crud_dataset
from schemas import dataset as schemas_dataset
from core import settings


def test_generating_dataset_metadata():
    username = 'username1'
    file_location1 = crud_dataset.generate_dataset_file_location(username=username)
    assert username in file_location1
    assert settings.USER_DATASET_LOCATION in file_location1
    file_location2 = crud_dataset.generate_dataset_file_location(username=username)
    assert file_location1 != file_location2


def test_create_datasetmeta(db: Session):
    datasetmeta_in = schemas_dataset.DataSetMetaCreate(filename='filenametest', user_id=1)
    datasetmeta = crud_dataset.create_datasetmeta(db, datasetmeta_in)
    assert datasetmeta.filename == datasetmeta_in.filename
    assert hasattr(datasetmeta, 'created_at')


def test_transforming_dataset(mocker):
    homeworld = {'name': 'testhomeworld'}
    homeworld_response = requests.Response()
    homeworld_response._content = b'{"name" : "testhomeworld"}'
    mocker.patch('crud.crud_dataset.request_session.get', return_value=homeworld_response)

    with open('tests/fixtures/dataset_page.json', 'r') as page_fixture:
        page = json.load(page_fixture)
        page_fixture.close()

    people = list(crud_dataset.transform_dataset(page))
    assert len(people) == len(page)
    person = people[0]
    assert person['homeworld'] == homeworld['name']
    assert type(person['date']) == datetime.date
    assert len(person) == len(settings.REQUIRED_DATASET_FIELDS)

    for key in person.keys():
        assert key in settings.REQUIRED_DATASET_FIELDS


def test_parsing_page(mocker):
    next_page_response = requests.Response()

    pages = [
        {'next': "1"},
        {'next': "2"},
        {'next': "3"},
        {'next': "4"},
    ]

    for page in pages:
        next_page_response._content = json.dumps(page).encode('utf-8')
        mocker.patch('crud.crud_dataset.request_session.get', return_value=next_page_response)
        result = crud_dataset.parse_page('url_str')
        assert next(result)['next'] == page['next']
