# Copyright 2026 Guzino (https://github.com/guzino)
# SPDX-License-Identifier: Apache-2.0

"""Cheap query heuristic for how many store hits to fetch. Not an LLM."""

from __future__ import annotations

import re

# Process language: advice or a visible-sample filter. Not eval topic words
# (startup, fusion, leaderboard, hire, ...).
_ADVICE = re.compile(
    r"\b(should|works?|always|best|guaranteed|advice|recommend|"
    r"playbook|tips)\b",
    re.I,
)
_SELECTION = re.compile(
    r"\b(only|published|famous|successful|stories|literature|"
    r"ranking|lessons|score)\b|based on|post-?mortems?",
    re.I,
)
_ARITH = re.compile(r"\d+\s*[+\-×x*/÷]\s*\d+")
_FACTOID = re.compile(
    r"boiling point|chemical formula|\bformula for\b|how many degrees",
    re.I,
)
_META = re.compile(r"\b(quote|define|insight)\b", re.I)
_METHOD = re.compile(r"\b(wald|survivorship|survivorship-bias)\b", re.I)


def suggested_retrieve_k(query: str, *, high: int = 5) -> int:
    """Return 0 for arithmetic/definitional controls, high for survivor-advice cues, else 1.

    Never exceeds `high`, so high=0 always means no store hits.
    """
    if high <= 0:
        return 0
    q = query.strip()
    if _ARITH.search(q) or _FACTOID.search(q):
        return 0
    if _META.search(q) and _METHOD.search(q):
        return 0
    if _ADVICE.search(q) or _SELECTION.search(q):
        return high
    return 1
