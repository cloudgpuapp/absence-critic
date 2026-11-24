# Copyright 2026 Guzino (https://github.com/guzino)
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

from absencecritic.prompts import (
    CRITIC_SYSTEM,
    DRAFT_SYSTEM,
    REVISE_SYSTEM,
    critic_user_message,
    revise_user_message,
)

OLLAMA_BASE_URL = "http://127.0.0.1:11434/v1"
OLLAMA_DEFAULT_MODEL = "qwen2.5:3b"


class OpenAICompat:
    """Chat Completions transport for GeneratorPort and CriticPort."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        *,
        allow_missing_key: bool = False,
    ):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.base_url = (
            base_url
            or os.environ.get("OPENAI_BASE_URL")
            or "https://api.openai.com/v1"
        ).rstrip("/")
        self.model = model or os.environ.get("ABSENCECRITIC_MODEL") or "gpt-4o-mini"
        if not self.api_key:
            if allow_missing_key or _is_ollama_url(self.base_url):
                self.api_key = "ollama"
            else:
                raise RuntimeError(
                    "OPENAI_API_KEY is not set. Use --provider fixture, "
                    "--provider ollama, or python -m absencecritic.adapters.cli.setup_ollama"
                )

    @classmethod
    def ollama(cls, model: str | None = None) -> OpenAICompat:
        return cls(
            api_key=os.environ.get("OPENAI_API_KEY") or "ollama",
            base_url=os.environ.get("OPENAI_BASE_URL") or OLLAMA_BASE_URL,
            model=model
            or os.environ.get("ABSENCECRITIC_MODEL")
            or OLLAMA_DEFAULT_MODEL,
            allow_missing_key=True,
        )

    def generate(self, *, query: str) -> str:
        return self._chat(DRAFT_SYSTEM, query, temperature=0.4, json_object=False)

    def critique(self, *, query: str, draft: str, store_hits: str) -> str:
        return self._chat(
            CRITIC_SYSTEM,
            critic_user_message(query, draft, store_hits),
            temperature=0.2,
            json_object=True,
        )

    def revise(self, *, query: str, draft: str, critique_json: str) -> str:
        return self._chat(
            REVISE_SYSTEM,
            revise_user_message(query, draft, critique_json),
            temperature=0.4,
            json_object=False,
        )

    def _chat(
        self, system: str, user: str, *, temperature: float, json_object: bool
    ) -> str:
        try:
            return self._post(system, user, temperature=temperature, json_object=json_object)
        except RuntimeError as exc:
            if json_object and (
                "response_format" in str(exc).lower() or _is_ollama_url(self.base_url)
            ):
                try:
                    return self._post(
                        system, user, temperature=temperature, json_object=False
                    )
                except RuntimeError:
                    raise exc from None
            raise

    def _post(
        self, system: str, user: str, *, temperature: float, json_object: bool
    ) -> str:
        payload: dict = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": temperature,
        }
        if json_object:
            payload["response_format"] = {"type": "json_object"}
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            self.base_url + "/chat/completions",
            data=data,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                body = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"OpenAI-compatible request failed: {exc} {detail}") from exc
        content = body["choices"][0]["message"].get("content")
        if not content:
            raise RuntimeError("OpenAI-compatible response had empty content")
        return content


def _is_ollama_url(url: str) -> bool:
    lowered = url.lower()
    return "11434" in lowered or "localhost:11434" in lowered or "127.0.0.1:11434" in lowered
