# Copyright 2026 Guzino (https://github.com/guzino)
# SPDX-License-Identifier: Apache-2.0

"""Cheap query heuristic for how many store hits to fetch. Not an LLM."""

from __future__ import annotations

_HIGH_CUES = (
    "startup",
    "founder",
    "publish",
    "diet",
    "nutrition",
    "disease",
    "post-mortem",
    "postmortem",
    "tricks",
    "launch",
    "supplement",
    "fusion",
    "leaderboard",
    "linkedin",
    "career",
    "guaranteed",
    "literature",
    "accuracy",
)


def suggested_retrieve_k(query: str, *, high: int = 5) -> int:
    """Return 0 for arithmetic/definitional controls, high for survivor-advice cues, else 1."""
    q = query.lower()
    compact = q.replace(" ", "")
    if "2+2" in compact:
        return 0
    if "boiling point" in q:
        return 0
    if "wald" in q and any(word in q for word in ("quote", "define", "insight")):
        return 0
    if any(cue in q for cue in _HIGH_CUES):
        return high
    return 1
