import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from ticket_app.analysis_provider import MockAnalysisProvider
from ticket_app.api import create_app

def load_policy():
    return json.loads(Path("scenarios/g02.json").read_text())

def load_fixtures():
    return json.loads(Path("tests/fixtures_g02.json").read_text())

@pytest.mark.parametrize("fixture", load_fixtures())
def test_g02_mock_fixtures(tmp_path, fixture):
    policy = load_policy()
    client = TestClient(
        create_app(
            provider=MockAnalysisProvider(),
            policy=policy,
            db_path=str(tmp_path / "test.db"),
        )
    )
    
    response = client.post(
        "/api/analyze",
        json={
            "subject": fixture["subject"],
            "text": fixture["text"],
        },
    )
    
    assert response.status_code == 200
    body = response.json()
    assert body["scenario"] == "g02"
    assert body["analysis"]["category"] == "wrong-category"
    assert body["analysis"]["priority"] == fixture["expected_priority"]
    assert body["requires_review"] is True

def test_g02_history_contains_successful_analysis(tmp_path):
    policy = load_policy()
    client = TestClient(
        create_app(
            provider=MockAnalysisProvider(),
            policy=policy,
            db_path=str(tmp_path / "test.db"),
        )
    )
    
    response = client.post(
        "/api/analyze",
        json={
            "subject": "Heating request",
            "text": "The radiator is cold and needs to be reviewed.",
        },
    )
    
    assert response.status_code == 200
    history = client.get("/api/history")
    assert history.status_code == 200
    assert len(history.json()) == 1
    assert history.json()[0]["analysis"]["category"] == "heating"