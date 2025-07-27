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

def test_get_projects_public():
    resp = client.get("/api/projects/")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

def test_add_project_admin(admin_token):
    data = {
        "title": "Test Project",
        "description": "A test project.",
        "thumbnail": "https://test.com/img.png",
        "technologies": ["Python"],
        "githubUrl": "https://github.com/test",
        "liveUrl": "https://test.com",
        "featured": False,
        "createdAt": "2024-01-01",
        "featuredAt": None
    }
    resp = client.post("/api/projects/", json=data, headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    result = resp.json()
    assert result["success"] is True
    global project_id
    project_id = result["project"]["id"]

def test_update_project_admin(admin_token):
    data = {
        "title": "Updated Project",
        "description": "Updated desc.",
        "thumbnail": "https://test.com/img.png",
        "technologies": ["Python", "FastAPI"],
        "githubUrl": "https://github.com/test",
        "liveUrl": "https://test.com",
        "featured": True,
        "createdAt": "2024-01-01",
        "featuredAt": "2024-01-02"
    }
    resp = client.put(f"/api/projects/{project_id}", json=data, headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    result = resp.json()
    assert result["success"] is True
    assert result["project"]["title"] == "Updated Project"

def test_delete_project_admin(admin_token):
    resp = client.delete(f"/api/projects/{project_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    result = resp.json()
    assert result["success"] is True

def test_add_project_unauthorized():
    data = {
        "title": "Test Project",
        "description": "A test project.",
        "thumbnail": "https://test.com/img.png",
        "technologies": ["Python"],
        "githubUrl": "https://github.com/test",
        "liveUrl": "https://test.com",
        "featured": False,
        "createdAt": "2024-01-01",
        "featuredAt": None
    }
    resp = client.post("/api/projects/", json=data)
    assert resp.status_code == 401 or resp.json().get("success") is False 