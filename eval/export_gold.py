# Copyright 2026 Guzino (https://github.com/guzino)
# SPDX-License-Identifier: Apache-2.0

"""Freeze fixture critiques as (query, draft, gold critique) JSONL for Phase 2."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from absencecritic.domain.models import Critique  # noqa: E402
from absencecritic.paths import default_fixture_path  # noqa: E402

GOLD_PATH = ROOT / "eval" / "gold" / "critiques.jsonl"
QUERIES_PATH = ROOT / "eval" / "queries.yaml"
PROVENANCE = "eval/fixtures/responses.yaml"


def _kinds() -> dict[str, str]:
    raw = yaml.safe_load(QUERIES_PATH.read_text(encoding="utf-8"))
    return {str(item["query"]).strip(): str(item["kind"]) for item in raw["queries"]}


def gold_records(fixture_path: Path | None = None) -> list[dict]:
    path = fixture_path or default_fixture_path()
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if isinstance(raw, dict):
        raw = raw.get("responses", [])
    if not isinstance(raw, list):
        raise ValueError(f"Expected a list of fixture responses in {path}")
    kinds = _kinds()
    records: list[dict] = []
    for item in raw:
        query = str(item["query"]).strip()
        critique = Critique.model_validate(item["critique"])
        records.append(
            {
                "query": query,
                "kind": kinds.get(query, "unknown"),
                "draft": str(item["draft"]),
                "critique": critique.model_dump(mode="json"),
                "provenance": PROVENANCE,
            }
        )
    records.sort(key=lambda row: row["query"])
    return records


def write_gold(dest: Path | None = None) -> Path:
    out = dest or GOLD_PATH
    out.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        json.dumps(row, ensure_ascii=False, sort_keys=True) for row in gold_records()
    ]
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


def main(argv: list[str] | None = None) -> int:
    del argv
    path = write_gold()
    print(path.as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
