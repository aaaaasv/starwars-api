from typing import List
from fastapi import APIRouter, BackgroundTasks, Depends, status, Query, HTTPException
from sqlalchemy.orm import Session
import petl as etl

from crud import crud_dataset, crud_user
from schemas import user as schemas_user
from schemas import dataset as schemas_dataset
from api.dependencies import get_db, check_availability
from core import settings

router = APIRouter()


@router.post('/')
def fetch_dataset_to_file(background_tasks: BackgroundTasks,
                          db: Session = Depends(get_db),
                          current_user: schemas_user.User = Depends(crud_user.get_current_user),
                          is_swapi_available: bool = Depends(check_availability)):
    if not is_swapi_available:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail='SWAPI is currently unavailable'
        )

    created_at, file_location = crud_dataset.generate_dataset_metadata(current_user.username)

    try:
        crud_dataset.create_csv_file(file_location)
    except FileNotFoundError:
        crud_dataset.create_base_user_dataset_dir(current_user.username)
        crud_dataset.create_csv_file(file_location)

    background_tasks.add_task(crud_dataset.fetch_dataset_to_file, file_location=file_location)
    crud_dataset.create_datasetmeta(db, datasetmeta=schemas_dataset.DataSetMetaCreate(
        filename=file_location.split('/')[-1], user_id=current_user.id))
    return status.HTTP_202_ACCEPTED


@router.get('/{dataset_id}', response_model=schemas_dataset.People)
def fetch_dataset_from_file(dataset_id: int,
                            limit: int = 10,
                            current_user: schemas_user.User = Depends(crud_user.get_current_user),
                            db: Session = Depends(get_db)):
    filename = crud_dataset.get_dataset_filename_by_id(db, dataset_id=dataset_id)
    file_location = f'{settings.USER_DATASET_LOCATION}/{current_user.username}/{filename}'
    try:
        dataset = crud_dataset.fetch_dataset_from_file_limited(file_location, limit)
        people = crud_dataset.structurize_dataset_table(dataset)
    except FileNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return {'people': people}


@router.get('/{dataset_id}/value_count',
            response_model=schemas_dataset.PeopleCounted,
            response_model_exclude_none=True)
def fetch_dataset_from_file_count(dataset_id: int,
                                  count_by: List[str] = Query(...),
                                  limit: int = 10,
                                  current_user: schemas_user.User = Depends(crud_user.get_current_user),
                                  db: Session = Depends(get_db)):
    filename = crud_dataset.get_dataset_filename_by_id(db, dataset_id=dataset_id)
    file_location = f'{settings.USER_DATASET_LOCATION}/{current_user.username}/{filename}'
    try:
        dataset_full = crud_dataset.fetch_dataset_from_file_full(file_location)
    except FileNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    try:
        dataset_count = crud_dataset.count_dataset_values(dataset_full, *count_by)
        dataset_limited = crud_dataset.limit_dataset(dataset_count, limit)
        people = crud_dataset.structurize_dataset_table(dataset_limited)
    except etl.errors.FieldSelectionError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    return {'people': people}
