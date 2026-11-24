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


class OpenAICompat:
    """Chat Completions transport for GeneratorPort and CriticPort."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
    ):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.base_url = (
            base_url
            or os.environ.get("OPENAI_BASE_URL")
            or "https://api.openai.com/v1"
        ).rstrip("/")
        self.model = model or os.environ.get("ABSENCECRITIC_MODEL") or "gpt-4o-mini"
        if not self.api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is not set. Tests and eval default to --provider fixture."
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
            with urllib.request.urlopen(req, timeout=120) as resp:
                body = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"OpenAI-compatible request failed: {exc} {detail}") from exc
        return body["choices"][0]["message"]["content"]
