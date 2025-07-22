import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fastapi.testclient import TestClient
from main import app
import pytest

client = TestClient(app)

ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin123"

@pytest.fixture(scope="session", autouse=True)
def setup_admin():
    # Reset admin credentials before running tests
    resp = client.post("/api/auth/reset-admin")
    assert resp.status_code == 200
    # Try to create the admin account before running tests
    resp = client.post("/api/auth/create-admin", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
    # Allow either success or already exists
    assert resp.status_code == 200
    assert resp.json()["success"] is True or resp.json()["message"] == "Admin account already exists." 