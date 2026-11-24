# Copyright 2026 Guzino (https://github.com/guzino)
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import os

from absencecritic.adapters.llm.openai_compat import OpenAICompat


class LocalCritic:
    """CriticPort only. Talks to a local OpenAI-compatible critic endpoint."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
    ):
        self._transport = OpenAICompat(
            api_key=api_key
            or os.environ.get("ABSENCECRITIC_LOCAL_API_KEY")
            or os.environ.get("OPENAI_API_KEY")
            or "local",
            base_url=base_url
            or os.environ.get("ABSENCECRITIC_LOCAL_BASE_URL")
            or "http://127.0.0.1:8080/v1",
            model=model
            or os.environ.get("ABSENCECRITIC_LOCAL_CRITIC_MODEL")
            or "absencecritic-critic",
        )
        self.model = self._transport.model
        self.base_url = self._transport.base_url

    def critique(self, *, query: str, draft: str, store_hits: str) -> str:
        return self._transport.critique(
            query=query, draft=draft, store_hits=store_hits
        )
