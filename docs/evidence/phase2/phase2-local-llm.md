# Phase 2 — Local LLM integration

## Purpose

This phase connects the starter application to a real local language model instead of using the mock provider.

The application keeps the same architecture provided in the starter project and extends the existing `LocalAnalysisProvider`.

## Local model

The model used for this phase is:

```text
qwen2.5-coder-1.5b-instruct
```

The model is executed locally through Bionic, using its OpenAI-compatible local API.

The local API is available at:

```text
http://localhost:1234/v1
```

## Environment configuration

The provided `.env.example` file was kept unchanged.

Local configuration was added only in the `.env` file used on the development machine.

The `.env` file contains:

```text
LLM_PROVIDER=local
SCENARIO_ID=g00
LLM_BASE_URL=http://localhost:1234/v1
LLM_MODEL=qwen2.5-coder-1.5b-instruct
LLM_API_KEY=
LLM_API_KEY_FILE=
LLM_TIMEOUT=60
DB_PATH=./data/analyses.db
API_URL=http://localhost:8000
```

The `.env` file is not intended to be committed to the repository.

## Local API validation

The local model API was first checked independently from the application.

The following endpoint was called:

```text
GET /v1/models
```

The API returned the installed model with the identifier:

```text
qwen2.5-coder-1.5b-instruct
```

A direct request to the OpenAI-compatible chat endpoint was then tested successfully:

```text
POST /v1/chat/completions
```

This confirmed that the local model was reachable before modifying the application code.

## Local provider implementation

The existing `LocalAnalysisProvider` in:

```text
src/ticket_app/analysis_provider.py
```

was extended instead of creating a new provider.

The provider now:

- sends the request to the local `/chat/completions` endpoint;
- provides the request and active scenario information to the model;
- asks the model to return structured JSON;
- parses the returned JSON;
- validates the result using the existing `Analysis` model;
- raises `ProviderUnavailable` if the local model server cannot be reached;
- raises `InvalidModelOutput` if the returned content cannot be validated.

The expected model output contains:

```text
summary
category
priority
next_action
```

## Request flow with the local model

The request now follows this path:

```text
User
  ↓
Streamlit
  ↓
FastAPI
  ↓
AnalysisService
  ↓
LocalAnalysisProvider
  ↓
Bionic local API
  ↓
Qwen 2.5 Coder 1.5B Instruct
  ↓
JSON response
  ↓
Pydantic validation
  ↓
Scenario validation
  ↓
SQLite storage
  ↓
Response displayed in Streamlit
```

## Validation

The FastAPI health endpoint confirmed that the application was using the local provider:

```json
{
  "status": "ok",
  "scenario": "g00",
  "provider": "local"
}
```

A full request was then tested from the Streamlit interface.

Example request:

```text
Subject:
Radiator not working

Request:
The radiator in room 204 is cold and does not heat the room.
```

The local model returned a structured analysis containing:

- a summary;
- a category;
- a priority;
- a next action;
- `requires_review = true`.

The result was also stored successfully in SQLite.

## Issue encountered

During the first end-to-end test, the API returned:

```text
HTTP 502 Bad Gateway
```

The local model was reachable, but its response could not be parsed as JSON.

The raw model output showed that the model wrapped the JSON response in Markdown code fences:

```text
```json
{
  "summary": "Radiator malfunction in room 204",
  "category": "general",
  "priority": "medium",
  "next_action": "Check radiator connections and replace if necessary"
}
```
```

The JSON parser expected the response to start directly with `{`, so the Markdown code fences caused the parsing step to fail.

## Correction

The local provider was updated to remove Markdown code fences before calling `json.loads()`.

The processing flow is now:

```text
Raw model response
  ↓
Remove optional Markdown code fences
  ↓
Parse JSON
  ↓
Validate with Analysis model
  ↓
Validate category against the scenario policy
```

This correction allows valid model responses wrapped in Markdown to be accepted while keeping the existing validation mechanisms.

Invalid or malformed responses are still rejected through `InvalidModelOutput`.

## Current status

At the end of this phase:

- the local API is reachable;
- the Qwen model is available through the OpenAI-compatible API;
- the application uses `LLM_PROVIDER=local`;
- a full request can be processed through the local LLM;
- the returned JSON is validated;
- the result is stored in SQLite;
- the result is displayed correctly in Streamlit.

The application is therefore ready for the next validation step: testing the behavior when the local model server is unavailable.

## Provider unavailable test

The local model server was intentionally stopped to verify error handling.

A request was then submitted from the Streamlit interface.

The application returned:

```text
HTTP 503 Service Unavailable
```

This confirms that an unavailable local model server is correctly converted into `ProviderUnavailable` and handled by FastAPI without crashing the application.