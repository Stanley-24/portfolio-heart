import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fastapi.testclient import TestClient
from main import app
import pytest

client = TestClient(app)
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin123"

@pytest.fixture
def admin_token():
    client.post("/api/auth/reset-admin")
    client.post("/api/auth/create-admin", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
    resp = client.post("/api/auth/login", data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
    assert resp.status_code == 200
    return resp.json()["access_token"]

def test_get_reviews_public():
    resp = client.get("/api/reviews/")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

def test_add_review_public():
    data = {"name": "Test User", "review": "Great!", "avatarUrl": "", "rating": 5}
    resp = client.post("/api/reviews/", json=data)
    assert resp.status_code == 200
    result = resp.json()
    assert result["success"] is True
    global review_id
    review_id = result["review"]["id"]

def test_update_review_admin(admin_token):
    data = {"name": "Test User", "review": "Updated!", "avatarUrl": "", "rating": 4}
    resp = client.put(f"/api/reviews/{review_id}", json=data, headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    result = resp.json()
    assert result["success"] is True
    assert result["review"]["review"] == "Updated!"

def test_delete_review_admin(admin_token):
    resp = client.delete(f"/api/reviews/{review_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    result = resp.json()
    assert result["success"] is True

def test_update_review_unauthorized():
    data = {"name": "Test User", "review": "Updated!", "avatarUrl": "", "rating": 4}
    resp = client.put(f"/api/reviews/123456", json=data)
    assert resp.status_code == 401 or resp.json().get("success") is False 