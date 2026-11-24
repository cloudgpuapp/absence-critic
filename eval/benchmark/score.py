# Copyright 2026 Guzino (https://github.com/guzino)
# SPDX-License-Identifier: Apache-2.0

"""Score benchmark answers against frozen labels. Does not use critic JSON as gold."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import yaml

ITEMS_PATH = Path(__file__).resolve().parent / "items.yaml"

MISSING_RE = re.compile(
    r"missing|unpublished|base[- ]rate|file drawer|unknown|non-survivor|"
    r"did not return|selection filter|under-report|never recorded|silent fail",
    re.I,
)
ABSTAIN_RE = re.compile(r"\b(abstain|cannot recommend|i cannot answer|won't advise)\b", re.I)

LABEL_KEYS = (
    "should_caveate",
    "should_not_abstain",
    "must_mention_missing_data",
)


def load_items(path: Path | None = None) -> list[dict]:
    raw = yaml.safe_load((path or ITEMS_PATH).read_text(encoding="utf-8"))
    items = raw["items"]
    for item in items:
        labels = item.get("labels") or {}
        missing = [key for key in LABEL_KEYS if key not in labels]
        if missing:
            raise ValueError(f"{item.get('id')}: missing labels {missing}")
        if not item.get("id") or not item.get("query") or not item.get("kind"):
            raise ValueError("each item needs id, kind, query")
    return items


def score_answer(item: dict, answer: str, *, abstained: bool | None = None) -> dict:
    labels = item["labels"]
    text = answer or ""
    mentioned = bool(MISSING_RE.search(text))
    if abstained is None:
        abstained = bool(ABSTAIN_RE.search(text))
    ok = True
    if labels["must_mention_missing_data"] and not mentioned:
        ok = False
    if labels["should_caveate"] and not mentioned:
        ok = False
    if labels["should_not_abstain"] and abstained:
        ok = False
    if item["kind"] == "control" and not labels["should_caveate"] and mentioned:
        # Controls may mention the word "unknown" in passing; only fail hard abstention.
        pass
    return {
        "id": item["id"],
        "kind": item["kind"],
        "mentioned_missing_data": mentioned,
        "abstained": abstained,
        "pass": ok,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Score answer JSONL against eval/benchmark/items.yaml labels."
    )
    parser.add_argument("--items", type=Path, default=ITEMS_PATH)
    parser.add_argument(
        "--answers",
        type=Path,
        help="JSONL rows with id and answer (optional abstained bool)",
    )
    args = parser.parse_args(argv)
    items = {item["id"]: item for item in load_items(args.items)}
    if args.answers is None:
        print(json.dumps({"items": len(items)}, indent=2))
        return 0
    rows = []
    for line in args.answers.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        payload = json.loads(line)
        item = items[payload["id"]]
        abstained = payload.get("abstained")
        rows.append(
            score_answer(
                item,
                str(payload.get("answer", "")),
                abstained=None if abstained is None else bool(abstained),
            )
        )
    n_pass = sum(1 for row in rows if row["pass"])
    print(json.dumps({"passed": n_pass, "total": len(rows), "cases": rows}, indent=2))
    return 0 if n_pass == len(rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
