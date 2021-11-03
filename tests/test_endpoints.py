import os
import uuid
from datetime import datetime, timezone
from typing import List

from fastapi.testclient import TestClient

# noinspection PyUnresolvedReferences
from .test_base import client, mock_get_db, create_test_database, test_db_session, clear_file_storage

PATH_1 = 'tests/test_images/image1.jpeg'
PATH_2 = 'tests/test_images/image2.jpeg'


def get_files_request_body(paths: List[str], image_format='image/jpeg'):
    """
    Builds post image request body
    """
    request = []
    for path in paths:
        file_request = ('images', (os.path.basename(path), open(path, 'rb'), image_format))
        request.append(file_request)
    return request


class TestPutEndpoint:

    def test_1_image_returns_201(self, client: TestClient):
        response = client.put('/frame/', files=get_files_request_body([PATH_1]))
        assert response.status_code == 201

    def test_2_images_returns_201(self, client: TestClient):
        response = client.put('/frame/', files=get_files_request_body([PATH_1, PATH_2]))
        assert response.status_code == 201

    def test_0_images_returns_422(self, client: TestClient):
        response = client.put('/frame/', files=get_files_request_body([]))
        assert response.status_code == 422

    def test_16_images_returns_403(self, client: TestClient):
        response = client.put('/frame/', files=get_files_request_body([PATH_1] * 16))
        assert response.status_code == 403

    def test_16_images_returns_detailed_error(self, client: TestClient):
        response = client.put('/frame/', files=get_files_request_body([PATH_1] * 16))
        assert response.json()['detail'] == 'No more than 15 images can be sent'

    def test_wrong_format_image_returns_403(self, client: TestClient):
        response = client.put('/frame/', files=get_files_request_body([PATH_1], 'image/psd'))
        assert response.status_code == 403

    def test_wrong_format_image_returns_detailed_error(self, client: TestClient):
        response = client.put('/frame/', files=get_files_request_body([PATH_1], 'image/psd'))
        assert response.json()['detail'] == "All images should have jpeg format"


class TestGetEndpoint:

    def test_get_images_by_valid_code_returns_200(self, client: TestClient):
        put_response = client.put('/frame/', files=get_files_request_body([PATH_1, PATH_2]))
        code = put_response.json()["request_code"]
        get_response = client.get(f'/frame/{code}')
        assert get_response.status_code == 200

    def test_get_images_by_valid_code_returns_valid_creation_date(self, client: TestClient):
        put_response = client.put('/frame/', files=get_files_request_body([PATH_1, PATH_2]))
        reference_creation_date = datetime.now(timezone.utc)
        code = put_response.json()["request_code"]
        get_response = client.get(f'/frame/{code}')
        real_creation_date = datetime.fromisoformat(get_response.json()[0]['created_at'])
        assert abs((reference_creation_date - real_creation_date).total_seconds()) < 1

    def test_get_images_by_non_valid_code_returns_404(self, client: TestClient):
        client.put('/frame/', files=get_files_request_body([PATH_1, PATH_2]))
        code = uuid.uuid4()
        get_response = client.get(f'/frame/{code}')
        assert get_response.status_code == 404

    def test_get_images_by_non_valid_code_returns_detailed_description(self, client: TestClient):
        client.put('/frame/', files=get_files_request_body([PATH_1, PATH_2]))
        code = uuid.uuid4()
        get_response = client.get(f'/frame/{code}')
        assert get_response.json()['detail'] == "Images not found"


class TestDeleteEndpoint:

    def test_delete_images_by_valid_code_returns_200(self, client: TestClient):
        put_response = client.put('/frame/', files=get_files_request_body([PATH_1]))
        code = put_response.json()["request_code"]
        delete_response = client.delete(f'/frame/{code}')
        assert delete_response.status_code == 200

    def test_delete_images_by_non_valid_code_returns_404(self, client: TestClient):
        client.put('/frame/', files=get_files_request_body([PATH_1]))
        code = uuid.uuid4()
        delete_response = client.delete(f'/frame/{code}')
        assert delete_response.status_code == 404

    def test_delete_images_by_non_valid_code_returns_detailed_error(self, client: TestClient):
        client.put('/frame/', files=get_files_request_body([PATH_1]))
        code = uuid.uuid4()
        delete_response = client.delete(f'/frame/{code}')
        assert delete_response.json()['detail'] == 'Images not found'
