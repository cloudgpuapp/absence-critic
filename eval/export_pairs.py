# Copyright 2026 Guzino (https://github.com/guzino)
# SPDX-License-Identifier: Apache-2.0

"""Export shielded vs unshielded preference pairs. Store bodies stay out of chosen."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import yaml

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from absencecritic.adapters.llm.fixture import FixtureLLM  # noqa: E402
from absencecritic.adapters.llm.openai_compat import OpenAICompat  # noqa: E402
from absencecritic.adapters.store.yaml_store import YamlStore  # noqa: E402
from absencecritic.application.loop import run  # noqa: E402
from absencecritic.domain.models import StoreCollection  # noqa: E402
from absencecritic.envfile import load_repo_env  # noqa: E402
from absencecritic.paths import default_fixture_path, default_store_dir  # noqa: E402

LICENSE_NOTE = (
    "Pairs measure shielded vs unshielded completions, not factual truth. "
    "Chosen text may still be wrong. Apache-2.0."
)
STORE_BODY_KEYS = ("summary", "non_survivor_evidence", "store_hits")


def private_entry_ids(store: YamlStore) -> set[str]:
    ids: set[str] = set()
    for entry in store.entries:
        source = (entry.source_path or "").replace("\\", "/")
        if entry.collection is StoreCollection.feedback or "/private/" in f"/{source}/":
            ids.add(entry.id)
    return ids


def strip_store_body(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: strip_store_body(item)
            for key, item in value.items()
            if key not in STORE_BODY_KEYS
        }
    if isinstance(value, list):
        return [strip_store_body(item) for item in value]
    return value


def make_pair(
    *,
    query_id: str,
    query: str,
    rejected: str,
    chosen: str,
    critique: Optional[dict],
    retrieved_ids: list[str],
    provider: str,
    model: str,
    private_ids: set[str],
    allow_private: bool = False,
    overlay: bool = False,
    now: Optional[datetime] = None,
) -> dict:
    leaked = set(retrieved_ids) & private_ids
    if leaked and not allow_private:
        raise ValueError(
            f"private store rows cannot appear in public export: {sorted(leaked)}"
        )
    meta = strip_store_body(critique) if critique else None
    stamp = (now or datetime.now(timezone.utc)).strftime("%Y-%m-%dT%H:%M:%SZ")
    return {
        "prompt": query,
        "rejected": rejected,
        "chosen": chosen,
        "critique": meta,
        "retrieved_ids": list(retrieved_ids),
        "query_id": query_id,
        "provider": provider,
        "model": model,
        "date": stamp,
        "overlay": overlay,
        "license_note": LICENSE_NOTE,
    }


def export_pairs(
    dest: Path,
    *,
    provider_name: str,
    queries_path: Path,
    allow_private: bool = False,
) -> Path:
    load_repo_env()
    provider = (
        FixtureLLM(default_fixture_path())
        if provider_name == "fixture"
        else OpenAICompat()
    )
    store = YamlStore(default_store_dir())
    private_ids = private_entry_ids(store)
    model = getattr(provider, "model", None) or type(provider).__name__
    queries = yaml.safe_load(queries_path.read_text(encoding="utf-8"))["queries"]
    dest.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    for item in queries:
        query = str(item["query"]).strip()
        baseline = run(query, provider=provider, store=store, shield=False)
        shielded = run(query, provider=provider, store=store, shield=True)
        critique = (
            shielded.critique.model_dump(mode="json") if shielded.critique else None
        )
        pair = make_pair(
            query_id=str(item["id"]),
            query=query,
            rejected=baseline.final,
            chosen=shielded.final,
            critique=critique,
            retrieved_ids=shielded.retrieved_ids,
            provider=provider_name,
            model=str(model),
            private_ids=private_ids,
            allow_private=allow_private,
        )
        lines.append(json.dumps(pair, ensure_ascii=False, sort_keys=True))
    dest.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return dest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Write preference pairs. Does not put store bodies in chosen."
    )
    parser.add_argument("--provider", choices=("fixture", "openai"), default="fixture")
    parser.add_argument("--queries", type=Path, default=ROOT / "eval" / "queries.yaml")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument(
        "--allow-private",
        action="store_true",
        help="Allow feedback/private store ids in retrieved_ids (off by default)",
    )
    args = parser.parse_args(argv)
    path = export_pairs(
        args.out,
        provider_name=args.provider,
        queries_path=args.queries,
        allow_private=args.allow_private,
    )
    print(path.as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
