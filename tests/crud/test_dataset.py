from sqlalchemy.orm import Session
import datetime
import requests
import json
import dateutil.parser
import copy
import petl as etl
import shutil
import os

from crud import crud_dataset
from schemas import dataset as schemas_dataset
from core import settings
from tests import conftest


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


def test_transforming_dataset(mocker, mocked_homeworld_url):
    with open('tests/fixtures/dataset_page.json', 'r') as page_fixture:
        page = json.load(page_fixture)
        page_fixture.close()

    people = list(crud_dataset.transform_dataset(page))
    assert len(people) == len(page)
    person = people[0]
    assert person['homeworld'] == 'testhomeworld'
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


def test_user_dataset_folder_creation(mocked_user_dataset_dir):
    assert crud_dataset.settings.USER_DATASET_LOCATION == conftest.TEST_DATASETS_DIR

    username = 'testuser'
    crud_dataset.create_base_user_dataset_dir(username)
    assert os.path.isdir(f'{conftest.TEST_DATASETS_DIR}/{username}')

    shutil.rmtree(conftest.TEST_DATASETS_DIR)


def test_csv_file_creation(mocked_user_dataset_dir):
    assert crud_dataset.settings.USER_DATASET_LOCATION == conftest.TEST_DATASETS_DIR

    username = 'testuser'
    crud_dataset.create_base_user_dataset_dir(username)
    file_location = crud_dataset.generate_dataset_file_location(username)
    crud_dataset.create_csv_file(file_location)
    assert os.path.isfile(file_location)

    table = etl.fromcsv(file_location)
    assert etl.header(table) == settings.REQUIRED_DATASET_FIELDS

    shutil.rmtree(conftest.TEST_DATASETS_DIR)


def test_dataset_fetching_to_file(mocker, mocked_user_dataset_dir, mocked_homeworld_url):
    assert crud_dataset.settings.USER_DATASET_LOCATION == conftest.TEST_DATASETS_DIR

    username = 'username1'

    crud_dataset.create_base_user_dataset_dir(username)
    file_location = crud_dataset.generate_dataset_file_location(username)
    crud_dataset.create_csv_file(file_location)

    with open('tests/fixtures/dataset_page_results.json', 'r') as page_fixture_file:
        page = json.load(page_fixture_file)
        source_page = copy.deepcopy(page)
        page_fixture_file.close()
    mocker.patch('crud.crud_dataset.parse_page', return_value=page)

    crud_dataset.fetch_dataset_to_file(file_location)
    result_table = crud_dataset.fetch_dataset_from_file_full(file_location).dicts()

    not_found_keys = set()

    for counter_person, person in enumerate(source_page):
        for key, value in person['results'][0].items():
            try:
                if key == 'edited':
                    assert result_table[counter_person]['date'] == str(dateutil.parser.parse(value).date())
                elif key == 'homeworld':
                    assert result_table[counter_person]['homeworld'] == 'testhomeworld'
                else:
                    assert result_table[counter_person][key] == value
            except KeyError:
                not_found_keys.add(key)

    for key in not_found_keys:
        assert key not in settings.REQUIRED_DATASET_FIELDS

    shutil.rmtree(conftest.TEST_DATASETS_DIR)


def test_get_dataset_info(db: Session):
    datasetmeta_info = {'filename': 'testfilename', 'user_id': 1}
    datasetmeta_create = schemas_dataset.DataSetMetaCreate(**datasetmeta_info)
    dataset = crud_dataset.create_datasetmeta(db, datasetmeta_create)

    file_location, owner_id = crud_dataset.get_dataset_info_by_id(db, dataset_id=dataset.id, username='testusername')

    assert file_location == f'{settings.USER_DATASET_LOCATION}/testusername/{datasetmeta_info["filename"]}'
    assert owner_id == datasetmeta_info['user_id']


def test_limit_dataset_table():
    full_row_num = 100
    table = etl.dummytable(numrows=100)
    assert len(etl.data(table)) == full_row_num
    limit_to_num = 23
    table_limited = crud_dataset.limit_dataset(table, limit_to_num)
    assert len(etl.data(table_limited)) == limit_to_num


def test_valued_dataset():
    expected_result = [
        ('male', 'Tatooine', 2, 0.4),
        ('n/a', 'Tatooine', 1, 0.2),
        ('n/a', 'Naboo', 1, 0.2),
        ('female', 'Alderaan', 1, 0.2),
    ]
    dataset = etl.fromjson('tests/fixtures/dataset_page.json')
    data = crud_dataset.count_dataset_values(dataset, 'gender',
                                             'homeworld')
    assert list(etl.data(data)) == expected_result

    data1 = crud_dataset.count_dataset_values(dataset, 'homeworld', 'eye_color')
    data2 = crud_dataset.count_dataset_values(dataset, 'eye_color', 'homeworld')
    assert etl.columns(data1)['count'] == etl.columns(data2)['count']
