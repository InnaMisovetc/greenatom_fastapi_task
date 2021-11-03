from typing import List
from uuid import UUID

from sqlalchemy.orm import Session

from db.models import ImageModel


def create_file_data(request_code: UUID, db: Session) -> ImageModel:
    """
    Saves file data to the database
    """
    db_image = ImageModel(request_code=request_code)
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image


def read_files_data(request_code: UUID, db: Session) -> List:
    """
    Get files data by unique request code
    """
    return db.query(ImageModel).filter(ImageModel.request_code == request_code).all()


def delete_file_data(db: Session, image_db: ImageModel) -> None:
    """
    Deletes file data from database by uuid
    """
    db.delete(image_db)
    db.commit()
