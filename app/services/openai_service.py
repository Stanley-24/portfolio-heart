import os
import requests
from dotenv import load_dotenv
load_dotenv()

def get_llama2_response(message, experience, projects):
    prompt = f"Experience: {experience}\nProjects: {projects}\n\nRecruiter: {message}\nStanley's Assistant:"
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama2",
            "prompt": prompt,
            "stream": False
        }
    )
    data = response.json()
    return data['response']

# Optional: Toggle between OpenAI and Ollama based on env
USE_OLLAMA = os.getenv("USE_OLLAMA", "true").lower() == "true"

# If you want to keep the same interface for your chatbot route:
def get_openai_response(message, experience, projects):
    if USE_OLLAMA:
        return get_llama2_response(message, experience, projects)
    # (You can keep the OpenAI code here for future use)
    raise Exception("OpenAI API not available. Set USE_OLLAMA=false and add OpenAI code if needed.") 