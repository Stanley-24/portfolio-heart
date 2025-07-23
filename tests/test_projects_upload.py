import os
import io
import pytest
from fastapi.testclient import TestClient
from app.main import app

def get_admin_token():
    # Replace with a valid admin JWT for local testing
    return "Bearer test_admin_jwt"

client = TestClient(app)

def test_upload_thumbnail_success(tmp_path):
    image_content = b"fake image data"
    file = io.BytesIO(image_content)
    file.name = "test.jpg"
    response = client.post(
        "/api/projects/upload-thumbnail",
        files={"file": ("test.jpg", file, "image/jpeg")},
        headers={"Authorization": get_admin_token()}
    )
    assert response.status_code == 200
    data = response.json()
    assert "url" in data
    # Optionally check file exists
    file_path = os.path.join("uploads/projects", "test.jpg")
    assert os.path.exists(file_path)
    # Clean up
    os.remove(file_path)

def test_upload_thumbnail_non_image():
    file = io.BytesIO(b"not an image")
    file.name = "test.txt"
    response = client.post(
        "/api/projects/upload-thumbnail",
        files={"file": ("test.txt", file, "text/plain")},
        headers={"Authorization": get_admin_token()}
    )
    assert response.status_code == 400

def test_upload_thumbnail_unauthorized():
    file = io.BytesIO(b"fake image data")
    file.name = "test.jpg"
    response = client.post(
        "/api/projects/upload-thumbnail",
        files={"file": ("test.jpg", file, "image/jpeg")}
        # No Authorization header
    )
    assert response.status_code == 401 