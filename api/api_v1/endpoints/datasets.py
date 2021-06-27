from fastapi import APIRouter, BackgroundTasks, Depends, status
from sqlalchemy.orm import Session

from crud import crud_dataset, crud_user
from schemas import user as schemas_user
from schemas import dataset as schemas_dataset
from api.dependencies import get_db

router = APIRouter()


@router.post('/')
def fetch_dataset_to_file(background_tasks: BackgroundTasks,
                          db: Session = Depends(get_db),
                          current_user: schemas_user.User = Depends(crud_user.get_current_user)):
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
