from types import SimpleNamespace

from fastapi.testclient import TestClient

import web_app


class FakeDbManager:
    def test_connection(self):
        return False


class FakeAIAgent:
    def __init__(self):
        self.calls = []

    def _chat_fallback(self, message, session_id, start_time):
        self.calls.append((message, session_id))
        return {
            "response": f"Resposta fallback para: {message}",
            "tokens_used": 0,
            "response_time": 0.1,
            "session_id": session_id,
            "mode": "fallback",
        }


class FakeIA:
    def __init__(self):
        self.db_manager = FakeDbManager()
        self.ai_agent = FakeAIAgent()
        self.config = SimpleNamespace(ai_name="Mamute")


client = TestClient(web_app.app)


def test_session_start_and_chat_work_without_database(monkeypatch):
    fake_ia = FakeIA()
    monkeypatch.setattr(web_app, "ia_system", fake_ia)
    monkeypatch.setattr(web_app, "db_ready", False)

    start_response = client.post("/session/start", json={"user_id": "tester"})

    assert start_response.status_code == 200
    session_id = start_response.json()["session_id"]
    assert session_id
    assert start_response.json()["mode"] == "degraded"

    chat_response = client.post(
        "/chat",
        json={
            "message": "Olá, como você está?",
            "session_id": session_id,
            "use_context": True,
        },
    )

    assert chat_response.status_code == 200
    payload = chat_response.json()
    assert payload["response"] == "Resposta fallback para: Olá, como você está?"
    assert payload["session_id"] == session_id
    assert payload["mode"] == "degraded"
    assert fake_ia.ai_agent.calls == [("Olá, como você está?", session_id)]
