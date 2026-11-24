# Copyright 2026 Guzino (https://github.com/guzino)
# SPDX-License-Identifier: Apache-2.0

"""Quarantine live critic runs. Promotion to gold is a human PR, not this module."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from absencecritic.application.jsonutil import parse_json_object  # noqa: E402
from absencecritic.application.retrieve import suggested_retrieve_k  # noqa: E402
from absencecritic.domain.models import Critique  # noqa: E402

INCOMING_DIR = ROOT / "eval" / "gold" / "incoming"
DEFAULT_INCOMING_PATH = INCOMING_DIR / "runs.jsonl"
GOLD_FILENAMES = frozenset(
    {
        "critiques.jsonl",
        "train.jsonl",
        "heldout.jsonl",
        "overlay.yaml",
        "splits.yaml",
    }
)
REQUIRED = (
    "provider",
    "model",
    "date",
    "query",
    "draft",
    "retrieved_ids",
    "raw_critique",
)


def assert_quarantine_path(path: Path) -> Path:
    if path.name in GOLD_FILENAMES:
        raise ValueError(
            f"incoming logs cannot write gold file {path.name}; "
            "promotion is a human pull request"
        )
    return path


def parse_incoming_row(raw: dict[str, Any]) -> dict[str, Any]:
    missing = [name for name in REQUIRED if name not in raw or raw[name] in (None, "")]
    if missing:
        raise ValueError(f"incoming row missing {missing}")
    retrieved = raw["retrieved_ids"]
    if not isinstance(retrieved, list) or any(not isinstance(x, str) for x in retrieved):
        raise ValueError("retrieved_ids must be a list of strings")
    critique_obj = raw.get("critique")
    parse_error = raw.get("parse_error")
    if critique_obj in (None, {}) and not parse_error:
        raise ValueError("incoming row needs critique or parse_error")
    if critique_obj not in (None, {}) and parse_error:
        raise ValueError("incoming row cannot have both critique and parse_error")
    critique_dump = None
    if critique_obj not in (None, {}):
        critique_dump = Critique.model_validate(critique_obj).model_dump(mode="json")
    return {
        "provider": str(raw["provider"]),
        "model": str(raw["model"]),
        "date": str(raw["date"]),
        "query": str(raw["query"]),
        "draft": str(raw["draft"]),
        "retrieved_ids": list(retrieved),
        "raw_critique": str(raw["raw_critique"]),
        "critique": critique_dump,
        "parse_error": None if not parse_error else str(parse_error),
    }


def append_incoming(path: Path, row: dict[str, Any]) -> Path:
    dest = assert_quarantine_path(path)
    parsed = parse_incoming_row(row)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(parsed, ensure_ascii=False, sort_keys=True) + "\n")
    return dest


def _model_name(provider: object) -> str:
    model = getattr(provider, "model", None)
    if model:
        return str(model)
    return type(provider).__name__


def capture_run(
    query: str,
    *,
    provider: object,
    store: object,
    provider_name: str,
    now: Optional[datetime] = None,
) -> dict[str, Any]:
    """Draft + retrieve + critique only. Does not revise and does not write gold."""
    gen = provider
    cri = provider
    draft = gen.generate(query=query)
    k = suggested_retrieve_k(query)
    hits = store.retrieve(query, draft, k=k)
    retrieved_ids = [entry.id for entry, _ in hits]
    raw_critique = cri.critique(
        query=query, draft=draft, store_hits=store.format_hits(hits)
    )
    critique_dump = None
    parse_error = None
    try:
        critique_dump = Critique.model_validate(
            parse_json_object(raw_critique)
        ).model_dump(mode="json")
    except Exception as exc:
        parse_error = str(exc)
    stamp = (now or datetime.now(timezone.utc)).strftime("%Y-%m-%dT%H:%M:%SZ")
    return parse_incoming_row(
        {
            "provider": provider_name,
            "model": _model_name(provider),
            "date": stamp,
            "query": query,
            "draft": draft,
            "retrieved_ids": retrieved_ids,
            "raw_critique": raw_critique,
            "critique": critique_dump,
            "parse_error": parse_error,
        }
    )
