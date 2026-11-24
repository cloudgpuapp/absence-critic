# Copyright 2026 Guzino (https://github.com/guzino)
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from absencecritic.adapters.llm.fixture import FixtureLLM
from absencecritic.adapters.llm.openai_compat import OpenAICompat
from absencecritic.adapters.store.yaml_store import YamlStore
from absencecritic.application.loop import run
from absencecritic.paths import default_fixture_path, default_store_dir


def _llm(name: str):
    if name == "fixture":
        return FixtureLLM(default_fixture_path())
    if name == "openai":
        return OpenAICompat()
    raise ValueError(f"Unknown provider: {name}")


def _default_provider_name() -> str:
    if os.environ.get("OPENAI_API_KEY"):
        return "openai"
    return "fixture"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="absencecritic",
        description="Run the AbsenceCritic Wald loop: draft → critic → revise.",
    )
    parser.add_argument("query", help="User question")
    parser.add_argument(
        "--no-shield",
        action="store_true",
        help="Return the primary draft only (baseline)",
    )
    parser.add_argument(
        "--show-critique",
        action="store_true",
        help="Print the structured critique after the answer",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="Print the full pipeline result as JSON",
    )
    parser.add_argument(
        "--provider",
        choices=("fixture", "openai"),
        default=_default_provider_name(),
        help="LLM backend (default: fixture unless OPENAI_API_KEY is set)",
    )
    parser.add_argument(
        "--store",
        type=Path,
        default=default_store_dir(),
        help="Directory of Non-Survivor Store YAML/JSONL files",
    )
    args = parser.parse_args(argv)

    store = YamlStore(args.store)
    result = run(
        args.query,
        provider=_llm(args.provider),
        store=store,
        shield=not args.no_shield,
    )
    if args.as_json:
        payload = {
            "query": result.query,
            "draft": result.draft,
            "retrieved_ids": result.retrieved_ids,
            "critique": result.critique.model_dump(mode="json") if result.critique else None,
            "final": result.final,
            "shielded": result.shielded,
        }
        print(json.dumps(payload, indent=2))
        return 0
    print(result.final)
    if args.show_critique and result.critique is not None:
        print("\n--- critique ---\n")
        print(json.dumps(result.critique.model_dump(mode="json"), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
