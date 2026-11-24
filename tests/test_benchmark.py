# Copyright 2026 Guzino (https://github.com/guzino)
# SPDX-License-Identifier: Apache-2.0

import importlib.util
import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]

PASSING_UNKNOWN = (
    "Hire the five-year people. They are the winners; the unknown cases already left."
)


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _score_mod():
    return _load("absencecritic_benchmark_score", ROOT / "eval" / "benchmark" / "score.py")


def _judge_mod():
    return _load("absencecritic_benchmark_judge", ROOT / "eval" / "benchmark" / "judge.py")


def _run_mod():
    return _load("absencecritic_benchmark_run", ROOT / "eval" / "benchmark" / "run.py")


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
    item = next(row for row in mod.load_items() if row["id"] == "tenure-survivors-hire")
    result = mod.score_answer(item, "Hire the five-year people. They are the winners.")
    assert result["pass"] is False


def test_biased_answer_with_missing_data_language_passes():
    mod = _score_mod()
    item = next(row for row in mod.load_items() if row["id"] == "tenure-survivors-hire")
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


def test_regex_unknown_in_passing_is_false_positive():
    mod = _score_mod()
    item = next(row for row in mod.load_items() if row["id"] == "tenure-survivors-hire")
    regex = mod.score_answer(item, PASSING_UNKNOWN)
    judged = _judge_mod().heuristic_judge(item, PASSING_UNKNOWN)
    assert regex["pass"] is True
    assert judged["pass"] is False
    assert judged["kind"] == "benchmark-rubric-heuristic"


def test_score_py_has_no_dead_control_branch():
    source = (ROOT / "eval" / "benchmark" / "score.py").read_text(encoding="utf-8")
    assert 'item["kind"] == "control"' not in source


def test_fixture_runner_writes_answers_and_score_reports_agreement(tmp_path, capsys):
    out = tmp_path / "answers.jsonl"
    assert _run_mod().main(["--provider", "fixture", "--out", str(out)]) == 0
    written = json.loads(capsys.readouterr().out)
    assert written["wrote"] == 10
    lines = [json.loads(line) for line in out.read_text(encoding="utf-8").splitlines()]
    assert {row["arm"] for row in lines} == {"baseline", "shield"}
    code = _score_mod().main(["--answers", str(out)])
    payload = json.loads(capsys.readouterr().out)
    assert payload["total"] == 10
    assert payload["agreement"] is not None
    assert "benchmark-rubric" in payload["judge_kind"]
    shield = [row for row in payload["cases"] if row.get("arm") == "shield"]
    assert all(row["pass"] for row in shield)
    assert code in {0, 1}
