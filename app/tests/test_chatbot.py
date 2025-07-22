import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/../'))
import pytest
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch

client = TestClient(app)

@patch("app.services.openai_service.get_openai_response")
def test_chatbot_smart_answer(mock_llm):
    mock_llm.return_value = "Stanley is open to remote work."
    resp = client.post("/api/chatbot/chatbot", json={"message": "Can you work from home?"})
    assert resp.status_code == 200
    assert "remote work" in resp.json()["answer"].lower()

@patch("app.services.openai_service.get_openai_response")
def test_chatbot_fallback(mock_llm):
    mock_llm.side_effect = Exception("LLM error")
    resp = client.post("/api/chatbot/chatbot", json={"message": "What is your favorite color?"})
    assert resp.status_code == 200
    assert "not sure" in resp.json()["answer"].lower() or "contact form" in resp.json()["answer"].lower() 