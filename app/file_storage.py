import os
import shutil
from datetime import datetime
from uuid import UUID

import aiofiles as aiof
from fastapi import UploadFile

from core.config import TEST_MODE
from db.models import ImageModel

BASE_DIR = 'data_test_mode' if TEST_MODE else 'data'


async def save_file_to_disk(image: UploadFile, db_image: ImageModel, extension: str = "jpg") -> str:
    """
    Saves image file under directory defined by database image model

    :return: Full path of the saved file
    """
    path = get_file_path(db_image.created_at, db_image.name, extension)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    async with aiof.open(path, "wb") as new_file:
        content = await image.read()
        await new_file.write(content)
        await new_file.flush()
    return path


def delete_file_from_disk(db_image: ImageModel, extension: str = "jpg") -> bool:
    """
    Deletes image file linked to provided database image model

    :return: True if file was deleted successfully, false otherwise.
    """
    path = get_file_path(db_image.created_at, db_image.name, extension)

    if not os.path.exists(path) or not os.path.isfile(path):
        return False

    dir_path = os.path.dirname(path)
    os.remove(path)
    if not os.listdir(dir_path):
        os.rmdir(dir_path)
    return True


def get_file_path(creation_date: datetime, image_name: UUID, extension: str) -> str:
    """
    Build file path accordingly to desired schema:
    <BASE_DIR>/<creation time formatted as %Y%m%d>>/<image name as UUID>.<image extension>
    """
    return os.path.join(BASE_DIR, datetime.strftime(creation_date, "%Y%m%d"), f"{image_name}.{extension}")


def clear():
    """
    Drop all data from BASE_DIR
    """
    shutil.rmtree(BASE_DIR)
