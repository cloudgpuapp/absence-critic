# Copyright 2026 Guzino (https://github.com/guzino)
# SPDX-License-Identifier: Apache-2.0

"""Validate critic train JSONL and export chat rows. Does not run a GPU job."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from absencecritic.domain.models import Critique  # noqa: E402
from absencecritic.prompts import CRITIC_SYSTEM, critic_user_message  # noqa: E402

DEFAULT_TRAIN = ROOT / "eval" / "gold" / "train.jsonl"
FORBIDDEN_NAMES = frozenset({"heldout.jsonl", "critiques.jsonl"})


def _refuse_eval_leak(path: Path) -> None:
    if path.name in FORBIDDEN_NAMES:
        raise ValueError(
            f"refusing {path.name}: train only on train.jsonl; "
            "held-out and the fixture union are not training data"
        )


def load_train_rows(path: Path) -> list[dict]:
    _refuse_eval_leak(path)
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
        for key in ("id", "query", "draft", "critique"):
            if key not in raw:
                raise ValueError(f"{path}:{i}: missing {key}")
        critique = Critique.model_validate(raw["critique"])
        rows.append(
            {
                "id": str(raw["id"]),
                "query": str(raw["query"]),
                "draft": str(raw["draft"]),
                "critique": critique.model_dump(mode="json"),
            }
        )
    if not rows:
        raise ValueError(f"{path}: no train rows")
    return rows


def to_chat_row(row: dict) -> dict:
    """Critic SFT example. Store hits are empty here; do not invent them."""
    critique_json = json.dumps(row["critique"], ensure_ascii=False, sort_keys=True)
    return {
        "id": row["id"],
        "messages": [
            {"role": "system", "content": CRITIC_SYSTEM},
            {
                "role": "user",
                "content": critic_user_message(row["query"], row["draft"], ""),
            },
            {"role": "assistant", "content": critique_json},
        ],
    }


def write_chat_jsonl(rows: list[dict], dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        json.dumps(to_chat_row(row), ensure_ascii=False, sort_keys=True) for row in rows
    ]
    dest.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return dest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate critic train JSONL. Fine-tune stays outside CI."
    )
    parser.add_argument("--train-jsonl", type=Path, default=DEFAULT_TRAIN)
    parser.add_argument(
        "--export-chat",
        type=Path,
        help="Write critic chat JSONL for an external trainer",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate only (default if --export-chat is omitted)",
    )
    args = parser.parse_args(argv)
    rows = load_train_rows(args.train_jsonl)
    if args.export_chat:
        write_chat_jsonl(rows, args.export_chat)
        print(args.export_chat.as_posix())
        return 0
    print(f"{len(rows)} critic train rows ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
