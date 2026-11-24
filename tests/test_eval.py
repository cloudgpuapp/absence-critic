# Copyright 2026 Guzino (https://github.com/guzino)
# SPDX-License-Identifier: Apache-2.0

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _eval_mod():
    eval_path = ROOT / "eval" / "run_eval.py"
    spec = importlib.util.spec_from_file_location("absencecritic_eval", eval_path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_fixture_eval_passes(capsys):
    assert _eval_mod().main(["--provider", "fixture"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["passed"] == payload["total"]
    case = next(row for row in payload["cases"] if row["id"] == "startup-launch")
    assert case["shared_draft"] is True
    drafts = {arm["draft"] for arm in case["arms"].values()}
    assert len(drafts) == 1
    assert set(case["arms"]) == {"baseline", "critic_only", "shield"}


def test_critic_only_arm_is_store_free(capsys):
    assert _eval_mod().main(["--provider", "fixture"]) == 0
    payload = json.loads(capsys.readouterr().out)
    for case in payload["cases"]:
        assert case["arms"]["critic_only"]["retrieved_ids"] == [], case["id"]


def test_fixture_eval_samples_reports_arm_spread(capsys):
    assert _eval_mod().main(["--provider", "fixture", "--samples", "2"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["samples"] == 2
    assert payload["arms"]["shield"]["spread"] == 0.0
    assert payload["arms"]["shield"]["mean"] == 1.0


def test_eval_records_error_and_continues(tmp_path, capsys):
    queries = tmp_path / "queries.yaml"
    queries.write_text(
        """
queries:
  - id: startup-launch
    kind: biased
    query: What works for launching a startup?
  - id: two-plus-two
    kind: control
    query: What is 2+2?
  - id: ml-tricks
    kind: biased
    query: Which ML tricks always improve accuracy?
""",
        encoding="utf-8",
    )
    mod = _eval_mod()
    real_run = mod.run

    def boom(query, **kwargs):
        if "2+2" in query:
            raise ValueError("invalid critique json")
        return real_run(query, **kwargs)

    mod.run = boom
    jsonl = tmp_path / "cases.jsonl"
    code = mod.main(
        [
            "--provider",
            "fixture",
            "--queries",
            str(queries),
            "--jsonl",
            str(jsonl),
        ]
    )
    assert code == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["total"] == 3
    assert payload["errored"] == 1
    assert payload["passed"] == 2
    by_id = {row["id"]: row for row in payload["cases"]}
    assert "error" in by_id["two-plus-two"]
    assert "ValueError" in by_id["two-plus-two"]["error"]
    assert by_id["startup-launch"]["pass"] is True
    assert by_id["ml-tricks"]["pass"] is True
    lines = [json.loads(line) for line in jsonl.read_text(encoding="utf-8").splitlines()]
    assert [row["id"] for row in lines] == [
        "startup-launch",
        "two-plus-two",
        "ml-tricks",
    ]
