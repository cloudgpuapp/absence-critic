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

GOLD_DIR = ROOT / "eval" / "gold"
GOLD_PATH = GOLD_DIR / "critiques.jsonl"
TRAIN_PATH = GOLD_DIR / "train.jsonl"
HELDOUT_PATH = GOLD_DIR / "heldout.jsonl"
SPLITS_PATH = GOLD_DIR / "splits.yaml"
QUERIES_PATH = ROOT / "eval" / "queries.yaml"
PROVENANCE = "eval/fixtures/responses.yaml"


def _query_index() -> dict[str, dict[str, str]]:
    raw = yaml.safe_load(QUERIES_PATH.read_text(encoding="utf-8"))
    index: dict[str, dict[str, str]] = {}
    for item in raw["queries"]:
        query = str(item["query"]).strip()
        index[query] = {"id": str(item["id"]), "kind": str(item["kind"])}
    return index


def load_splits(path: Path | None = None) -> tuple[list[str], list[str]]:
    raw = yaml.safe_load((path or SPLITS_PATH).read_text(encoding="utf-8"))
    train = [str(x) for x in raw["train"]]
    heldout = [str(x) for x in raw["heldout"]]
    overlap = set(train) & set(heldout)
    if overlap:
        raise ValueError(f"split ids in both train and heldout: {sorted(overlap)}")
    if not train or not heldout:
        raise ValueError("train and heldout lists must both be non-empty")
    return train, heldout


def _dump_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [json.dumps(row, ensure_ascii=False, sort_keys=True) for row in rows]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def gold_records(fixture_path: Path | None = None) -> list[dict]:
    path = fixture_path or default_fixture_path()
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if isinstance(raw, dict):
        raw = raw.get("responses", [])
    if not isinstance(raw, list):
        raise ValueError(f"Expected a list of fixture responses in {path}")
    index = _query_index()
    records: list[dict] = []
    for item in raw:
        query = str(item["query"]).strip()
        meta = index.get(query)
        if meta is None:
            raise ValueError(f"fixture query has no eval/queries.yaml id: {query!r}")
        critique = Critique.model_validate(item["critique"])
        records.append(
            {
                "id": meta["id"],
                "query": query,
                "kind": meta["kind"],
                "draft": str(item["draft"]),
                "critique": critique.model_dump(mode="json"),
                "provenance": PROVENANCE,
            }
        )
    records.sort(key=lambda row: row["id"])
    return records


def _partition(records: list[dict]) -> tuple[list[dict], list[dict]]:
    train_ids, heldout_ids = load_splits()
    train_set, heldout_set = set(train_ids), set(heldout_ids)
    gold_ids = {row["id"] for row in records}
    missing = (train_set | heldout_set) - gold_ids
    extra = gold_ids - train_set - heldout_set
    if missing:
        raise ValueError(f"splits.yaml ids not in gold: {sorted(missing)}")
    if extra:
        raise ValueError(f"gold ids missing from splits.yaml: {sorted(extra)}")
    heldout_kinds = {row["kind"] for row in records if row["id"] in heldout_set}
    if "biased" not in heldout_kinds or "control" not in heldout_kinds:
        raise ValueError("heldout must include at least one biased and one control id")
    train = [row for row in records if row["id"] in train_set]
    heldout = [row for row in records if row["id"] in heldout_set]
    return train, heldout


def write_gold(dest: Path | None = None) -> Path:
    records = gold_records()
    train, heldout = _partition(records)
    out = dest or GOLD_PATH
    _dump_jsonl(out, records)
    _dump_jsonl(out.parent / TRAIN_PATH.name, train)
    _dump_jsonl(out.parent / HELDOUT_PATH.name, heldout)
    return out


def main(argv: list[str] | None = None) -> int:
    del argv
    path = write_gold()
    print(path.as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
