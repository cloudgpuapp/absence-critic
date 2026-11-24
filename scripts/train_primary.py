# Copyright 2026 Guzino (https://github.com/guzino)
# SPDX-License-Identifier: Apache-2.0

"""Validate preference-pair JSONL for a primary-model DPO job. No GPU in CI."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STORE_BODY_KEYS = ("summary", "non_survivor_evidence", "store_hits")
REQUIRED = ("prompt", "rejected", "chosen")


def load_pair_rows(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    rows: list[dict] = []
    for i, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            raw = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{i}: invalid JSON") from exc
        if not isinstance(raw, dict):
            raise ValueError(f"{path}:{i}: row must be a JSON object")
        if "messages" in raw and "prompt" not in raw:
            raise ValueError(
                f"{path}:{i}: this looks like critic SFT chat, not generator pairs"
            )
        missing = [name for name in REQUIRED if not str(raw.get(name, "")).strip()]
        if missing:
            raise ValueError(f"{path}:{i}: missing {missing}")
        critique = raw.get("critique")
        if isinstance(critique, dict) and _has_store_body(critique):
            raise ValueError(f"{path}:{i}: critique still contains store body fields")
        rows.append(
            {
                "prompt": str(raw["prompt"]),
                "rejected": str(raw["rejected"]),
                "chosen": str(raw["chosen"]),
                "query_id": str(raw.get("query_id", "")),
            }
        )
    if not rows:
        raise ValueError(f"{path}: no pair rows")
    return rows


def _has_store_body(value: object) -> bool:
    if isinstance(value, dict):
        if any(key in value for key in STORE_BODY_KEYS):
            return True
        return any(_has_store_body(item) for item in value.values())
    if isinstance(value, list):
        return any(_has_store_body(item) for item in value)
    return False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate generator preference pairs. Training stays outside CI."
    )
    parser.add_argument("--pairs", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true", help="Validate only")
    args = parser.parse_args(argv)
    rows = load_pair_rows(args.pairs)
    print(f"{len(rows)} preference pairs ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
