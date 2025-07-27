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
    # Reset and create admin before login
    client.post("/api/auth/reset-admin")
    client.post("/api/auth/create-admin", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
    resp = client.post("/api/auth/login", data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
    assert resp.status_code == 200
    return resp.json()["access_token"]

def test_get_experience_public():
    resp = client.get("/api/experience/")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

def test_add_experience_admin(admin_token):
    data = {
        "dateRange": "2023-2024",
        "title": "Test Engineer",
        "company": "TestCorp",
        "url": "https://test.com",
        "icon": "link",
        "colorScheme": "blue"
    }
    resp = client.post("/api/experience/", json=data, headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    result = resp.json()
    assert result["success"] is True
    assert result["experience"]["title"] == "Test Engineer"
    global experience_id
    experience_id = result["experience"]["id"]

def test_update_experience_admin(admin_token):
    data = {
        "dateRange": "2023-2025",
        "title": "Updated Engineer",
        "company": "TestCorp",
        "url": "https://test.com",
        "icon": "link",
        "colorScheme": "yellow"
    }
    resp = client.put(f"/api/experience/{experience_id}", json=data, headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    result = resp.json()
    assert result["success"] is True
    assert result["experience"]["title"] == "Updated Engineer"

def test_delete_experience_admin(admin_token):
    resp = client.delete(f"/api/experience/{experience_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    result = resp.json()
    assert result["success"] is True

def test_add_experience_unauthorized():
    data = {
        "dateRange": "2023-2024",
        "title": "Test Engineer",
        "company": "TestCorp",
        "url": "https://test.com",
        "icon": "link",
        "colorScheme": "blue"
    }
    resp = client.post("/api/experience/", json=data)
    assert resp.status_code == 401 or resp.json().get("success") is False 