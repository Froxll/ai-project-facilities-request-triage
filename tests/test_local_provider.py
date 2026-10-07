import json

import httpx
import pytest

from ticket_app.analysis_models import Request
from ticket_app.analysis_provider import (
    InvalidModelOutput,
    LocalAnalysisProvider,
    ProviderUnavailable,
)


POLICY = {
    "id": "g02",
    "categories": ["electrical", "plumbing", "heating"],
    "instructions": "Route the request to the correct maintenance category.",
}


def test_local_provider_sends_expected_payload_and_parses_response():
    captured = {}

    def handler(request: httpx.Request):
        captured["payload"] = json.loads(request.content.decode())

        model_output = {
            "summary": "Radiator is not heating correctly.",
            "category": "heating",
            "priority": "medium",
            "next_action": "Ask the heating maintenance team to review the request.",
        }

        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(model_output)
                        }
                    }
                ]
            },
            request=request,
        )

    transport = httpx.MockTransport(handler)

    provider = LocalAnalysisProvider(
        base_url="http://localhost:1234/v1",
        model="test-model",
        timeout=5,
        transport=transport,
    )

    result = provider.analyze(
        Request(
            subject="Radiator not working",
            text="The radiator in room 204 is cold and does not heat the room.",
        ),
        POLICY,
    )

    payload = captured["payload"]

    assert payload["model"] == "test-model"
    assert payload["temperature"] == 0
    assert payload["max_tokens"] == 300

    assert payload["messages"][0]["role"] == "system"
    assert payload["messages"][1]["role"] == "user"

    user_data = json.loads(payload["messages"][1]["content"])

    assert user_data["subject"] == "Radiator not working"
    assert (
        user_data["text"]
        == "The radiator in room 204 is cold and does not heat the room."
    )

    assert result.category == "heating"
    assert result.priority == "medium"


def test_local_provider_timeout_becomes_provider_unavailable():
    def handler(request: httpx.Request):
        raise httpx.ReadTimeout("Model timed out", request=request)

    transport = httpx.MockTransport(handler)

    provider = LocalAnalysisProvider(
        base_url="http://localhost:1234/v1",
        model="test-model",
        timeout=1,
        transport=transport,
    )

    with pytest.raises(ProviderUnavailable):
        provider.analyze(
            Request(
                subject="Water leak",
                text="There is water leaking in the main corridor.",
            ),
            POLICY,
        )


def test_local_provider_rejects_malformed_json():
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

    transport = httpx.MockTransport(handler)

    provider = LocalAnalysisProvider(
        base_url="http://localhost:1234/v1",
        model="test-model",
        timeout=5,
        transport=transport,
    )

    with pytest.raises(InvalidModelOutput):
        provider.analyze(
            Request(
                subject="Power problem",
                text="There is no power in the meeting room.",
            ),
            POLICY,
        )