import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch

client = TestClient(app)

@patch("app.services.openai_service.get_openai_response")
def test_chatbot_smart_answer(mock_llm):
    mock_llm.return_value = "Stanley is open to remote work."
    resp = client.post("/api/chatbot/chatbot", json={"message": "Can you work from home?"})
    assert resp.status_code == 200
    # Accept any answer mentioning remote work or remote opportunities
    answer = resp.json()["answer"].lower()
    assert "remote" in answer and ("opportunit" in answer or "work" in answer)

@patch("app.services.openai_service.get_openai_response")
def test_chatbot_fallback(mock_llm):
    mock_llm.side_effect = Exception("LLM error")
    resp = client.post("/api/chatbot/chatbot", json={"message": "What is your favorite color?"})
    assert resp.status_code == 200
    # Accept any answer mentioning color or help (matches fallback logic)
    answer = resp.json()["answer"].lower()
    assert "color" in answer or "help" in answer 