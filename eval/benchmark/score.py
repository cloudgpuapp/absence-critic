# Copyright 2026 Guzino (https://github.com/guzino)
# SPDX-License-Identifier: Apache-2.0

"""Score benchmark answers against frozen labels. Does not use critic JSON as gold."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

import yaml

_BENCH_DIR = Path(__file__).resolve().parent
if str(_BENCH_DIR) not in sys.path:
    sys.path.insert(0, str(_BENCH_DIR))
from judge import judge_answer  # noqa: E402

ITEMS_PATH = _BENCH_DIR / "items.yaml"

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
ITEM_KEYS = ("id", "kind", "domain", "annotator", "query")
# Labels from these annotators are not independent of the prompts and store.
NON_INDEPENDENT_ANNOTATORS = frozenset({"guzino", "agent-draft"})


def load_items(path: Path | None = None) -> list[dict]:
    raw = yaml.safe_load((path or ITEMS_PATH).read_text(encoding="utf-8"))
    items = raw["items"]
    seen: set[str] = set()
    for item in items:
        absent = [key for key in ITEM_KEYS if not item.get(key)]
        if absent:
            raise ValueError(f"{item.get('id')}: missing {absent}")
        if item["id"] in seen:
            raise ValueError(f"duplicate benchmark id: {item['id']}")
        seen.add(item["id"])
        labels = item.get("labels") or {}
        missing = [key for key in LABEL_KEYS if key not in labels]
        if missing:
            raise ValueError(f"{item.get('id')}: missing labels {missing}")
    return items


def item_stats(items: list[dict]) -> dict:
    def count(key: str) -> dict[str, int]:
        return dict(sorted(Counter(str(item[key]) for item in items).items()))

    independent = [
        item["id"]
        for item in items
        if item["annotator"] not in NON_INDEPENDENT_ANNOTATORS
    ]
    return {
        "items": len(items),
        "kinds": count("kind"),
        "domains": len({item["domain"] for item in items}),
        "annotators": count("annotator"),
        "independent_label_items": len(independent),
    }


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
        help="JSONL rows with id and answer (optional arm, abstained bool)",
    )
    parser.add_argument(
        "--judge",
        choices=("none", "heuristic", "openai"),
        default="heuristic",
        help="Rubric judge beside the regex scorer (never the critic under test)",
    )
    args = parser.parse_args(argv)
    loaded = load_items(args.items)
    items = {item["id"]: item for item in loaded}
    if args.answers is None:
        print(json.dumps(item_stats(loaded), indent=2))
        return 0
    rows = []
    for line in args.answers.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        payload = json.loads(line)
        item = items[payload["id"]]
        abstained = payload.get("abstained")
        abstained_flag = None if abstained is None else bool(abstained)
        answer = str(payload.get("answer", ""))
        regex = score_answer(item, answer, abstained=abstained_flag)
        judged = judge_answer(
            item, answer, abstained=abstained_flag, kind=args.judge
        )
        row = dict(regex)
        if payload.get("arm"):
            row["arm"] = payload["arm"]
        row["regex_pass"] = regex["pass"]
        row["judge"] = judged
        if judged.get("pass") is None:
            row["agree"] = None
        else:
            row["agree"] = bool(regex["pass"]) == bool(judged["pass"])
        rows.append(row)
    n_pass = sum(1 for row in rows if row["pass"])
    judged_rows = [row for row in rows if row["judge"].get("pass") is not None]
    n_agree = sum(1 for row in judged_rows if row["agree"])
    payload_out = {
        "passed": n_pass,
        "total": len(rows),
        "judge_kind": None if args.judge == "none" else judged_rows[0]["judge"]["kind"]
        if judged_rows
        else args.judge,
        "agreement": (n_agree / len(judged_rows)) if judged_rows else None,
        "cases": rows,
    }
    print(json.dumps(payload_out, indent=2))
    return 0 if n_pass == len(rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
