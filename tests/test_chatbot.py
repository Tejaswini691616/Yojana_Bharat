# PATH: GovScheme/tests/test_chatbot.py
import json
import uuid


def _register_and_login(client):
    email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    client.post("/register", data={
        "full_name": "Chat Tester", "email": email, "password": "Passw0rd!",
        "age": "22", "annual_income": "60000", "caste": "General",
        "farmer": "No", "student": "Yes", "disabled": "No",
        "senior_citizen": "No", "bpl": "No", "widow": "No",
    }, follow_redirects=True)
    return email


def test_chat_message_returns_reply(client):
    _register_and_login(client)
    resp = client.post("/api/chat/message", json={"message": "What schemes do you recommend for me?"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert "reply" in data
    assert data["intent"] == "RECOMMENDATIONS"


def test_chat_empty_message_rejected(client):
    resp = client.post("/api/chat/message", json={"message": ""})
    assert resp.status_code == 400


def test_chat_languages_endpoint(client):
    resp = client.get("/api/chat/languages")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "English" in data["text_languages"]
    assert "Hindi" in data["text_languages"]


def test_voice_input_without_provider_returns_503(client):
    from io import BytesIO
    data = {"audio": (BytesIO(b"fake audio bytes"), "test.webm"), "language": "English"}
    resp = client.post("/api/chat/voice-input", data=data, content_type="multipart/form-data")
    assert resp.status_code == 503
