# Copyright 2026 Guzino (https://github.com/guzino)
# SPDX-License-Identifier: Apache-2.0

import importlib.util
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def _score_mod():
    path = ROOT / "eval" / "benchmark" / "score.py"
    spec = importlib.util.spec_from_file_location("absencecritic_benchmark_score", path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _query_ids() -> set[str]:
    queries = yaml.safe_load((ROOT / "eval" / "queries.yaml").read_text(encoding="utf-8"))
    splits = yaml.safe_load((ROOT / "eval" / "gold" / "splits.yaml").read_text(encoding="utf-8"))
    ids = {item["id"] for item in queries["queries"]}
    ids.update(splits["train"])
    ids.update(splits["heldout"])
    return ids


def test_benchmark_ids_disjoint_from_gold_and_fixture_eval():
    mod = _score_mod()
    items = mod.load_items()
    bench_ids = {item["id"] for item in items}
    overlap = bench_ids & _query_ids()
    assert not overlap
    kinds = {item["kind"] for item in items}
    assert "biased" in kinds
    assert "control" in kinds


def test_benchmark_queries_are_absent_from_src_and_tests():
    items = _score_mod().load_items()
    roots = (ROOT / "src", ROOT / "tests")
    for item in items:
        query = item["query"]
        for root in roots:
            for path in root.rglob("*"):
                if not path.is_file() or path.suffix not in {".py", ".md", ".yaml"}:
                    continue
                text = path.read_text(encoding="utf-8")
                assert query not in text, f"{item['id']} copied into {path}"


def test_scorer_does_not_read_critique_json():
    mod = _score_mod()
    source = (ROOT / "eval" / "benchmark" / "score.py").read_text(encoding="utf-8")
    assert "survivorship_risk" not in source
    assert "Critique" not in source


def test_control_answer_passes_without_missing_data_language():
    mod = _score_mod()
    item = next(row for row in mod.load_items() if row["id"] == "water-formula")
    result = mod.score_answer(item, "H2O")
    assert result["pass"] is True


def test_biased_answer_without_caveat_fails():
    mod = _score_mod()
    item = next(row for row in mod.load_items() if row["id"] == "decade-stayer-shortlist")
    result = mod.score_answer(item, "Pick the decade stayers. They are the winners.")
    assert result["pass"] is False


def test_biased_answer_with_missing_data_language_passes():
    mod = _score_mod()
    item = next(row for row in mod.load_items() if row["id"] == "decade-stayer-shortlist")
    result = mod.score_answer(
        item,
        "That sample is missing people who left. The unpublished exits are the non-survivors.",
    )
    assert result["pass"] is True


def test_control_must_not_abstain():
    mod = _score_mod()
    item = next(row for row in mod.load_items() if row["id"] == "triangle-degrees")
    result = mod.score_answer(item, "I abstain; selection filters prevent an answer.")
    assert result["pass"] is False
