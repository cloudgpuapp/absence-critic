# Copyright 2026 Guzino (https://github.com/guzino)
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import Protocol


class LLMProvider(Protocol):
    def complete(self, *, system: str, user: str, stage: str, query: str) -> str:
        """Return model text for draft, critique, or revise."""
