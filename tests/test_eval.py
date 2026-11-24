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


def test_fixture_eval_passes():
    assert _eval_mod().main(["--provider", "fixture"]) == 0


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
