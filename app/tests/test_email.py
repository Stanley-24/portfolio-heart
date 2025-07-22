import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/../'))
import pytest
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch

client = TestClient(app)

@patch("app.services.email_service.send_resume_with_zoho")
def test_send_resume(mock_send_email):
    mock_send_email.return_value = None
    resp = client.post("/api/email/send_resume", json={"email": "test@example.com"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "sent"
    mock_send_email.assert_called_once() 