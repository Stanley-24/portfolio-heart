import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fastapi.testclient import TestClient
from main import app
import pytest

client = TestClient(app)
ADMIN_EMAIL = "owarieta24@gmail.com"
ADMIN_PASSWORD = "admin123"

@pytest.fixture
def admin_token():
    client.post("/api/auth/reset-admin")
    client.post("/api/auth/create-admin", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
    resp = client.post("/api/auth/login", data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
    assert resp.status_code == 200
    return resp.json()["access_token"]

def test_upload_resume_admin(admin_token):
    file_content = b"%PDF-1.4 test pdf file"
    files = {"file": ("resume.pdf", file_content, "application/pdf")}
    resp = client.post("/api/resume/upload", files=files, headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    result = resp.json()
    assert result["success"] is True

def test_get_resume_file_public():
    resp = client.get("/api/resume/file")
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"

def test_save_resume_analytics_admin(admin_token):
    resp = client.post("/api/resume/save", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    result = resp.json()
    assert result["success"] is True

def test_get_resume_stats_admin(admin_token):
    resp = client.get("/api/resume/stats", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    result = resp.json()
    assert result["success"] is True

def test_delete_resume_admin(admin_token):
    resp = client.delete("/api/resume/", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    result = resp.json()
    assert result["success"] is True

def test_upload_resume_unauthorized():
    file_content = b"%PDF-1.4 test pdf file"
    files = {"file": ("resume.pdf", file_content, "application/pdf")}
    resp = client.post("/api/resume/upload", files=files)
    assert resp.status_code == 401 or resp.json().get("success") is False 