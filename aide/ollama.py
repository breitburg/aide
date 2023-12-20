import requests
import json
from typing import Optional, Any
from dataclasses import dataclass


class Ollama:
    def __init__(self, base_url=None):
        self.base_url = base_url if base_url is not None else "http://localhost:11434"

    def generate(
        self,
        prompt: str,
        model: str,
        system: Optional[str] = None,
        format: Optional[str] = None,
        stream: bool = True,
        context: Optional[list[int]] = None,
        raw: bool = False,
    ):
        url = self.base_url + "/api/generate"

        headers = {"Content-Type": "application/json"}
        data = {
            "prompt": prompt,
            "model": model,
            "system": system,
            "stream": stream,
            "context": context,
            "format": format,
            "raw": raw,
        }

        response = requests.post(
            url,
            headers=headers,
            data=json.dumps(data, default=str),
            stream=True,
        )

        for chunk in response.iter_lines():
            yield CompletionChunk.from_dict(json.loads(chunk.decode("utf-8")))

    def ask(
        self,
        prompt: str,
        model: str,
        system: Optional[str] = None,
        format: Optional[str] = None,
        context: Optional[list[int]] = None,
    ) -> "CompletionChunk":
        chunks = list(self.generate(prompt, model, system, format, False, context))
        if chunks:
            return chunks[-1]

        return None


@dataclass
class CompletionDetails:
    total_duration: Optional[int]
    load_duration: Optional[int]
    sample_count: Optional[int]
    sample_duration: Optional[int]
    prompt_eval_count: Optional[int]
    prompt_eval_duration: Optional[int]
    eval_count: Optional[int]
    eval_duration: Optional[int]
    context: Optional[list[int]]

    @property
    def speed(self):
        if self.eval_count and self.eval_duration:
            return self.eval_count / self.eval_duration

        return None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CompletionDetails":
        return cls(
            total_duration=data.get("total_duration"),
            load_duration=data.get("load_duration"),
            sample_count=data.get("sample_count"),
            sample_duration=data.get("sample_duration"),
            prompt_eval_count=data.get("prompt_eval_count"),
            prompt_eval_duration=data.get("prompt_eval_duration"),
            eval_count=data.get("eval_count"),
            eval_duration=data.get("eval_duration"),
            context=data.get("context"),
        )


@dataclass
class CompletionChunk:
    text: str
    model: str
    created_at: str
    details: Optional[CompletionDetails]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CompletionChunk":
        details = CompletionDetails.from_dict(data)

        return cls(
            model=data.get("model"),
            created_at=data.get("created_at"),
            text=data.get("response"),
            details=details if data.get("done") else None,
        )
