# Phase 1 — Request flow

## Purpose

This document describes how a request moves through the starter application before the integration of the local LLM.

## Request flow

```text
User
  ↓
Streamlit interface
ui/app.py
  ↓
POST /api/analyze
  ↓
FastAPI
api.py
  ↓
Request validation
  ↓
AnalysisService
analysis_service.py
  ↓
AnalysisProvider
analysis_provider.py
  ↓
Scenario validation
  ↓
Record creation
  ↓
SQLite storage
storage.py
  ↓
JSON response returned to Streamlit
```

## Main components

### `ui/app.py`

The Streamlit interface collects the request subject and description.

It sends the data to the API using:

```text
POST /api/analyze
```

The JSON response returned by the API is then displayed to the user.

---

### `api.py`

The API is the main entry point of the backend.

It:

- loads the active scenario;
- selects the configured provider;
- receives and validates the request;
- calls the analysis service;
- handles provider errors;
- creates the final record;
- stores the result;
- returns the response to the interface.

---

### `analysis_service.py`

The analysis service calls the selected provider.

It also checks that the category returned by the provider belongs to the list of categories allowed by the active scenario.

If the category is not valid, the result is rejected.

---

### `analysis_provider.py`

This file defines the common interface used by the analysis providers.

Two providers are currently available:

- `MockAnalysisProvider`: used for deterministic testing;
- `LocalAnalysisProvider`: reserved for the local LLM integration in Phase 2.

The local provider is not implemented yet in the starter project.

---

### `storage.py`

The storage layer uses SQLite.

Each completed analysis is stored as a JSON payload in the `analyses` table.

The API can also retrieve the 20 most recent records through:

```text
GET /api/history
```

## Validation points

Several validation steps are present in the application:

| Validation       | Location           |
| ---------------- | ------------------ |
| Request format   | FastAPI / Pydantic |
| Provider output  | `Analysis` model   |
| Allowed category | `AnalysisService`  |
| Persistence      | `Store.save()`     |

## Current Phase 1 configuration

The application is currently running with:

```text
LLM_PROVIDER=mock
SCENARIO_ID=g00
```

The local LLM provider will be implemented in Phase 2.