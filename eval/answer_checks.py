# Copyright 2026 Guzino (https://github.com/guzino)
# SPDX-License-Identifier: Apache-2.0

"""Checks on final answers shared by the eval and benchmark scorers."""

from __future__ import annotations

import re

# The user never sees a draft, critique, or store; final answers must not talk about them.
PIPELINE_LEAK_RE = re.compile(
    r"\b(the|this|your) draft\b|\brevised (version|answer|draft)\b|"
    r"\b(no|nothing)\s+(\S+\s+){0,2}retrieved\b|\bstore (hits?|entries)\b|"
    r"\bthe critique\b|\bwald module\b",
    re.I,
)


def leaks_pipeline(text: str | None) -> bool:
    return bool(PIPELINE_LEAK_RE.search(text or ""))
