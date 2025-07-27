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

def test_subscribe_newsletter_public():
    data = {"email": "test@example.com", "is_active": True}
    resp = client.post("/api/newsletter/subscribe", json=data)
    assert resp.status_code == 200
    result = resp.json()
    assert result["success"] is True
    global subscriber_id
    subscriber_id = result["subscriber"]["id"]

def test_unsubscribe_newsletter_public():
    resp = client.post(f"/api/newsletter/unsubscribe/{subscriber_id}")
    assert resp.status_code == 200
    result = resp.json()
    assert result["success"] is True

def test_get_subscribers_admin(admin_token):
    resp = client.get("/api/newsletter/", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

def test_update_subscriber_admin(admin_token):
    data = {"email": "test@example.com", "is_active": False}
    resp = client.put(f"/api/newsletter/{subscriber_id}", json=data, headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    result = resp.json()
    assert result["success"] is True

def test_delete_subscriber_admin(admin_token):
    resp = client.delete(f"/api/newsletter/{subscriber_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    result = resp.json()
    assert result["success"] is True

def test_update_subscriber_unauthorized():
    data = {"email": "test@example.com", "is_active": False}
    resp = client.put(f"/api/newsletter/123456", json=data)
    assert resp.status_code == 401 or resp.json().get("success") is False 