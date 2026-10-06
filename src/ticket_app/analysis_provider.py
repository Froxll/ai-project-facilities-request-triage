from typing import Protocol

from ticket_app.analysis_models import Analysis, Request


class ProviderUnavailable(RuntimeError):
    pass


class InvalidModelOutput(RuntimeError):
    pass


class AnalysisProvider(Protocol):
    def analyze(self, request: Request, policy: dict) -> Analysis: ...


class MockAnalysisProvider:
    def analyze(self, request: Request, policy: dict) -> Analysis:
        return Analysis(
            summary=f"{request.subject}: {request.text}"[:240],
            category=policy["categories"][0],
            priority="medium",
            next_action="Ask a reviewer to route the request.",
        )


class LocalAnalysisProvider:
    def __init__(self, base_url, model, timeout=60, key="", transport=None):
        self.base_url, self.model, self.timeout = base_url, model, timeout
        self.key, self.transport = key, transport

    def analyze(self, request: Request, policy: dict) -> Analysis:
        import json
        import httpx
        from pydantic import ValidationError

        system_prompt = (
            "You are a request classification assistant. "
            "Return only valid JSON with exactly these fields: "
            "summary, category, priority, next_action. "
            f"The allowed categories are: {policy['categories']}. "
            "Priority must be one of: low, medium, high. "
            "Do not include markdown, comments, or additional text."
        )

        user_payload = {
            "subject": request.subject,
            "text": request.text,
            "instructions": policy.get("instructions", ""),
        }

        headers = {}
        if self.key:
            headers["Authorization"] = f"Bearer {self.key}"

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(user_payload)},
            ],
            "temperature": 0,
        }

        try:
            with httpx.Client(
                timeout=self.timeout,
                transport=self.transport,
            ) as client:
                response = client.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=headers,
                )
                response.raise_for_status()

        except (httpx.RequestError, httpx.HTTPStatusError) as exc:
            raise ProviderUnavailable(
                f"Local model server unavailable: {exc}"
            ) from exc

        try:
            data = response.json()
            content = data["choices"][0]["message"]["content"].strip()

            if content.startswith("```"):
                lines = content.splitlines()

                if lines[0].startswith("```"):
                    lines = lines[1:]

                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]

                content = "\n".join(lines).strip()

            parsed = json.loads(content)
            return Analysis.model_validate(parsed)

        except (
            KeyError,
            IndexError,
            json.JSONDecodeError,
            ValidationError,
            TypeError,
        ) as exc:
            raise InvalidModelOutput(
                "Local model returned invalid structured output"
            ) from exc