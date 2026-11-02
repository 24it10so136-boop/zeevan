import os
from pathlib import Path
os.environ["DATABASE_URL"] = "sqlite:///./test_zeevan.db"
os.environ["JWT_SECRET"] = "test-secret"
os.environ["CORS_ORIGINS"] = "http://localhost:5173"
Path("test_zeevan.db").unlink(missing_ok=True)
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_full_local_api_flow():
    assert client.get("/api/health").json()["status"] == "ok"
    assert client.get("/api/model").json()["available"] is True
    assert len(client.get("/api/phases").json()["phases"]) == 3
    email = "local-test@example.com"
    registered = client.post("/api/auth/register", json={"full_name": "Local Tester", "email": email, "password": "password123"})
    assert registered.status_code == 200
    token = registered.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    check = client.post("/api/symptoms/check", headers=headers, json={"description": "I have a dull headache and feel tired", "selected": ["Headache"]})
    assert check.status_code == 200
    check_id = check.json()["id"]
    assert len(check.json()["questions"]) == 3
    result = client.post(f"/api/symptoms/check/{check_id}/analyze", headers=headers, json={"answers": {"duration": "1–3 days", "severity": "Mild", "fever": "No"}})
    assert result.status_code == 200
    assert result.json()["demo"] is True
    assert result.json()["urgent"] is False
    assert "headache" in result.json()["nlp_extracted_symptoms"]
    assert len(result.json()["predictions"]) > 0
    assert result.json()["model"]["available"] is True
    saved = client.post(f"/api/symptoms/{check_id}/save", headers=headers)
    assert saved.status_code == 200
    journeys = client.get("/api/journeys", headers=headers)
    assert journeys.status_code == 200
    assert journeys.json()[0]["id"] == check_id

def test_phase_three_safety_engine_is_independent():
    check = client.post("/api/symptoms/check", json={"description": "I have severe difficulty breathing", "selected": []})
    assert check.status_code == 200
    result = client.post(f"/api/symptoms/check/{check.json()['id']}/analyze", json={"answers": {}})
    assert result.status_code == 200
    assert result.json()["urgent"] is True
    assert "severe_breathing" in result.json()["urgent_reasons"]
