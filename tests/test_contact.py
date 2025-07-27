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

def test_book_call_public():
    data = {
        "name": "Test User",
        "email": "test@example.com",
        "preferred_datetime": "2024-08-01T10:00:00Z",
        "video_call_provider": "zoom"
    }
    resp = client.post("/api/contact/book", json=data)
    assert resp.status_code == 200
    result = resp.json()
    assert result["success"] is True
    global call_id
    call_id = result["call"]["id"]

def test_send_message_public():
    data = {"name": "Test User", "email": "test@example.com", "message": "Hello!"}
    resp = client.post("/api/contact/message", json=data)
    assert resp.status_code == 200
    result = resp.json()
    assert result["success"] is True

def test_list_bookings_admin(admin_token):
    resp = client.get("/api/contact/bookings", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

def test_list_messages_admin(admin_token):
    resp = client.get("/api/contact/messages", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    assert isinstance(resp.json(), list) 