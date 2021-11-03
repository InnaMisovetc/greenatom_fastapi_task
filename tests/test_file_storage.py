import uuid
from datetime import datetime

import pytest
from fastapi import UploadFile

from app import file_storage as fs
from db.models import ImageModel

PATH_1 = 'tests/test_images/image1.jpeg'


class TestFileStorage:
    @pytest.mark.asyncio
    async def test_file_saved_correctly(self):
        upload_file = UploadFile("image1.jpeg", open(PATH_1, 'rb'), "image/jpeg")
        image_model = ImageModel(name=uuid.uuid4(), created_at=datetime.now(), request_code=uuid.uuid4())
        new_image_path = await fs.save_file_to_disk(upload_file, image_model)
        assert open(new_image_path, 'rb').read() == open(PATH_1, 'rb').read()

    @pytest.mark.asyncio
    async def test_file_deleted_correctly(self):
        upload_file = UploadFile("image1.jpeg", open(PATH_1, 'rb'), "image/jpeg")
        image_model = ImageModel(name=uuid.uuid4(), created_at=datetime.now(), request_code=uuid.uuid4())
        await fs.save_file_to_disk(upload_file, image_model)
        assert fs.delete_file_from_disk(image_model) is True
