# Copyright 2026 Guzino (https://github.com/guzino)
# SPDX-License-Identifier: Apache-2.0

"""Compare baseline vs shielded answers using fixtures (no API key).

Regenerate live fixtures later:
  set OPENAI_API_KEY
  python -c "from eval.record_fixtures import main; main()"
  (or run each query with --provider openai --json and paste into
  eval/fixtures/responses.yaml)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from absencecritic.pipeline import run  # noqa: E402
from absencecritic.providers.fixture import FixtureProvider  # noqa: E402
from absencecritic.providers.openai_compat import OpenAICompatibleProvider  # noqa: E402
from absencecritic.store import NonSurvivorStore  # noqa: E402

MISSING_RE = re.compile(
    r"surviv|missing|unpublished|base rate|file drawer|unknown|caveat|"
    r"did not return|non-survivor|selection|under-report|failure rate",
    re.I,
)


def load_queries(path: Path) -> list[dict]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))["queries"]


def score_case(item: dict, shielded, baseline) -> dict:
    kind = item["kind"]
    critique = shielded.critique
    text = shielded.final
    missing_lang = bool(MISSING_RE.search(text or ""))
    used_store = False
    if critique and shielded.retrieved_ids:
        used = {h.id for h in critique.non_survivors}
        used_store = bool(used & set(shielded.retrieved_ids)) or bool(critique.non_survivors)
    adjustment = (
        critique.confidence_adjustment.value if critique else None
    )
    control_ok = True
    biased_ok = True
    if kind == "control":
        control_ok = adjustment != "abstain" and (critique is None or critique.survivorship_risk < 0.5)
    else:
        biased_ok = missing_lang and adjustment in {"lower", "seek_more_data", "abstain"}
    return {
        "id": item["id"],
        "kind": kind,
        "retrieved_ids": shielded.retrieved_ids,
        "survivorship_risk": critique.survivorship_risk if critique else None,
        "confidence_adjustment": adjustment,
        "missing_data_language": missing_lang,
        "used_store_ids": used_store,
        "baseline_chars": len(baseline.final),
        "shielded_chars": len(shielded.final),
        "pass": control_ok if kind == "control" else biased_ok,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="AbsenceCritic Phase 0 eval")
    parser.add_argument("--provider", choices=("fixture", "openai"), default="fixture")
    parser.add_argument("--queries", type=Path, default=ROOT / "eval" / "queries.yaml")
    args = parser.parse_args(argv)

    provider = (
        FixtureProvider(ROOT / "eval" / "fixtures" / "responses.yaml")
        if args.provider == "fixture"
        else OpenAICompatibleProvider()
    )
    store = NonSurvivorStore(ROOT / "data" / "non_survivors")
    rows = []
    for item in load_queries(args.queries):
        q = item["query"]
        baseline = run(q, provider=provider, store=store, shield=False)
        shielded = run(q, provider=provider, store=store, shield=True)
        rows.append(score_case(item, shielded, baseline))

    n_pass = sum(1 for r in rows if r["pass"])
    print(json.dumps({"passed": n_pass, "total": len(rows), "cases": rows}, indent=2))
    return 0 if n_pass == len(rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
