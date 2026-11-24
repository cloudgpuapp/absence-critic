# Copyright 2026 Guzino (https://github.com/guzino)
# SPDX-License-Identifier: Apache-2.0

"""Log a critic run to the gold incoming quarantine (not train.jsonl)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

EVAL = Path(__file__).resolve().parent
ROOT = EVAL.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
if str(EVAL) not in sys.path:
    sys.path.insert(0, str(EVAL))

import yaml  # noqa: E402

from absencecritic.adapters.llm.fixture import FixtureLLM  # noqa: E402
from absencecritic.adapters.llm.openai_compat import OpenAICompat  # noqa: E402
from absencecritic.adapters.store.yaml_store import YamlStore  # noqa: E402
from absencecritic.envfile import load_repo_env  # noqa: E402
from absencecritic.paths import default_fixture_path, default_store_dir  # noqa: E402

from incoming import DEFAULT_INCOMING_PATH, append_incoming, capture_run  # noqa: E402


def _queries(args: argparse.Namespace) -> list[str]:
    if args.query:
        return [args.query]
    raw = yaml.safe_load(args.queries.read_text(encoding="utf-8"))
    return [str(item["query"]).strip() for item in raw["queries"]]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Quarantine critic JSONL. Does not promote to gold."
    )
    parser.add_argument("--provider", choices=("fixture", "openai"), default="fixture")
    parser.add_argument("--query", default="")
    parser.add_argument("--queries", type=Path)
    parser.add_argument("--out", type=Path, default=DEFAULT_INCOMING_PATH)
    args = parser.parse_args(argv)
    if not args.query and args.queries is None:
        parser.error("pass --query or --queries")
    load_repo_env()
    provider = (
        FixtureLLM(default_fixture_path())
        if args.provider == "fixture"
        else OpenAICompat()
    )
    store = YamlStore(default_store_dir())
    for query in _queries(args):
        row = capture_run(
            query, provider=provider, store=store, provider_name=args.provider
        )
        append_incoming(args.out, row)
    print(args.out.as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
