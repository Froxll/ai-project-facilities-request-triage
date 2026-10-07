# Contributions

This project was developed collaboratively using feature branches and Pull Requests.

## Nathalie / Main integration

Main contributions:

- initial project setup and local Python environment;
- validation of the starter application;
- analysis of the existing architecture;
- implementation of the local LLM integration;
- configuration and validation of the local OpenAI-compatible API;
- implementation of structured model output parsing;
- handling of Markdown-wrapped JSON responses;
- validation of HTTP 502 and 503 error handling;
- integration and testing of the Group 02 scenario;
- local model evaluation;
- review and merge of team Pull Requests;
- project documentation.

## Team member A

Main contributions:

- creation of the Group 02 scenario;
- update of `group.txt` to `g02`;
- creation of `scenarios/g02.json`;
- definition of:
  - `electrical`;
  - `plumbing`;
  - `heating`;
- definition of deterministic scenario keywords;
- configuration of high-priority vocabulary;
- Pull Request for scenario integration.

## Team member B

Main contributions:

- extension of `MockAnalysisProvider`;
- deterministic routing based on scenario keywords;
- addition of the six supplied Group 02 fixtures;
- addition of Group 02 mock tests;
- update of baseline tests to explicitly use the mock provider;
- verification that tests run without the local LLM;
- Pull Request for mock and fixture integration.

## Collaboration workflow

The team used:

- `main` as the integration branch;
- dedicated feature branches;
- Pull Requests before merging;
- peer review before integration;
- automated tests before accepting changes.

Main feature branches included:

```text
feature/g02-scenario
feature/g02-mock-fixtures
```

All merged changes were reviewed before being integrated into `main`.