import json
from pathlib import Path

import httpx
from fastapi.testclient import TestClient

from ticket_app.analysis_models import Analysis
from ticket_app.analysis_provider import LocalAnalysisProvider
from ticket_app.api import create_app


def load_policy():
    return json.loads(Path("scenarios/g02.json").read_text())


class UnknownCategoryProvider:
    def analyze(self, request, policy):
        return Analysis(
            summary="The request was analysed successfully.",
            category="payroll",
            priority="medium",
            next_action="Ask a human reviewer to inspect this request.",
        )


def test_unknown_category_returns_502_and_is_not_saved(tmp_path):
    client = TestClient(
        create_app(
            provider=UnknownCategoryProvider(),
            policy=load_policy(),
            db_path=str(tmp_path / "test.db"),
        )
    )

    response = client.post(
        "/api/analyze",
        json={
            "subject": "Radiator problem",
            "text": "The radiator in room 204 does not heat the room.",
        },
    )

    assert response.status_code == 502

    history = client.get("/api/history")

    assert history.status_code == 200
    assert history.json() == []


def test_model_timeout_returns_503_and_is_not_saved(tmp_path):
    def handler(request: httpx.Request):
        raise httpx.ReadTimeout("Model timed out", request=request)

    provider = LocalAnalysisProvider(
        base_url="http://localhost:1234/v1",
        model="test-model",
        timeout=1,
        transport=httpx.MockTransport(handler),
    )

    client = TestClient(
        create_app(
            provider=provider,
            policy=load_policy(),
            db_path=str(tmp_path / "test.db"),
        )
    )

    response = client.post(
        "/api/analyze",
        json={
            "subject": "Water leak",
            "text": "There is water leaking from a pipe in the corridor.",
        },
    )

    assert response.status_code == 503

    history = client.get("/api/history")

    assert history.status_code == 200
    assert history.json() == []


def test_malformed_model_output_returns_502_and_is_not_saved(tmp_path):
    def handler(request: httpx.Request):
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": "this is not valid json"
                        }
                    }
                ]
            },
            request=request,
        )

    provider = LocalAnalysisProvider(
        base_url="http://localhost:1234/v1",
        model="test-model",
        timeout=5,
        transport=httpx.MockTransport(handler),
    )

    client = TestClient(
        create_app(
            provider=provider,
            policy=load_policy(),
            db_path=str(tmp_path / "test.db"),
        )
    )

    response = client.post(
        "/api/analyze",
        json={
            "subject": "Electrical problem",
            "text": "There is no power in the meeting room.",
        },
    )

    assert response.status_code == 502

    history = client.get("/api/history")

    assert history.status_code == 200
    assert history.json() == []