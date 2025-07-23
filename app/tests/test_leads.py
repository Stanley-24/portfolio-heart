import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/../'))
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.contact import Lead
from app.core.database import SessionLocal, Base, engine
from app.routes.auth import get_current_admin

client = TestClient(app)

# Mock admin dependency for tests
def override_get_current_admin():
    return True
app.dependency_overrides[get_current_admin] = override_get_current_admin

@pytest.fixture(autouse=True)
def setup_and_teardown_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_create_and_get_lead():
    data = {"name": "Test Recruiter", "email": "recruiter@example.com", "interest": "Resume Request"}
    resp = client.post("/api/leads", json=data)
    assert resp.status_code == 201
    lead_id = resp.json()["id"]
    # Get all leads
    resp = client.get("/api/leads")
    assert resp.status_code == 200
    assert any(lead["id"] == lead_id for lead in resp.json())
    # Get single lead
    resp = client.get(f"/api/leads/{lead_id}")
    assert resp.status_code == 200
    assert resp.json()["email"] == "recruiter@example.com"
    # Update lead
    update = {"name": "Updated Name", "email": "updated@example.com", "interest": "Updated"}
    resp = client.patch(f"/api/leads/{lead_id}", json=update)
    assert resp.status_code == 200
    assert resp.json()["name"] == "Updated Name"
    # Delete lead
    resp = client.delete(f"/api/leads/{lead_id}")
    assert resp.status_code == 204
    # Confirm deletion
    resp = client.get(f"/api/leads/{lead_id}")
    assert resp.status_code == 404 