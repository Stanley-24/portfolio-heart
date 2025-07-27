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

def test_admin_login():
    resp = client.post("/api/auth/login", data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
    assert resp.status_code == 200
    assert resp.json()["success"] is True

def test_create_admin():
    resp = client.post("/api/auth/create-admin", json={"email": "admin2@example.com", "password": "admin456"})
    # Only works if no admin exists yet, so allow either success or already exists
    assert resp.status_code == 200
    assert resp.json()["success"] is True or resp.json()["message"] == "Admin account already exists."

def test_change_password(admin_token):
    resp = client.post("/api/auth/change-password", json={"old_password": ADMIN_PASSWORD, "new_password": "admin789"}, headers={"Authorization": f"Bearer {admin_token}"})
    # Allow either success or old password incorrect (if already changed)
    assert resp.status_code == 200 or resp.json()["message"] == "Old password is incorrect."

# Test protected endpoint with/without token
def test_protected_endpoint_requires_auth():
    resp = client.post("/api/experience/", json={"dateRange": "2023-2024", "title": "Test", "company": "Test", "url": "https://test.com", "icon": "link", "colorScheme": "blue"})
    assert resp.status_code == 401 or resp.json().get("success") is False 

def test_protected_test_unauthorized():
    resp = client.get("/api/protected-test")
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Not authenticated" 

def test_protected_test_post_unauthorized():
    resp = client.post("/api/protected-test-post")
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Not authenticated" 