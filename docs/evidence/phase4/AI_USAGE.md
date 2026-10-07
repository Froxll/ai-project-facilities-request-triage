# AI Usage

AI tools were used as development support during this project.

## Tools used

The main AI assistant used during the project was ChatGPT.

## How AI was used

AI assistance was used for:

- understanding and reformulating the project requirements;
- explaining the starter architecture and request flow;
- clarifying the role of FastAPI, Streamlit, SQLite, pytest, Docker, Jenkins and Terraform;
- helping identify where the starter project should be extended rather than rewritten;
- suggesting implementation approaches for the local LLM provider;
- helping debug integration issues with the local model API;
- helping diagnose invalid JSON responses returned by the model;
- proposing test cases and documentation structure;
- helping prepare Git workflow and contribution tracking;
- reviewing implementation steps against the project requirements.

## Example of AI-assisted debugging

During the local LLM integration, the application initially returned HTTP 502 errors.

The model output was inspected and showed that valid JSON was wrapped in Markdown code fences.

AI assistance helped identify the parsing issue and suggested removing optional Markdown code fences before calling `json.loads()`.

The change was then implemented, tested locally, and validated through the complete application flow.

## Human validation

AI-generated suggestions were not used without verification.

All changes were:

- reviewed before being applied;
- tested locally;
- checked against the supplied project requirements;
- validated with pytest where applicable;
- manually tested through the application when required.

The team remained responsible for all implementation, integration and final decisions.