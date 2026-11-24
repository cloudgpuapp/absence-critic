# Copyright 2026 Guzino (https://github.com/guzino)
# SPDX-License-Identifier: Apache-2.0

import importlib.util
import json
from pathlib import Path

import pytest

from absencecritic.adapters.llm.fixture import FixtureLLM
from absencecritic.adapters.store.yaml_store import YamlStore
from absencecritic.paths import default_fixture_path, default_store_dir

ROOT = Path(__file__).resolve().parents[1]


def _incoming_mod():
    path = ROOT / "eval" / "incoming.py"
    spec = importlib.util.spec_from_file_location("absencecritic_incoming", path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _log_mod():
    path = ROOT / "eval" / "log_incoming.py"
    spec = importlib.util.spec_from_file_location("absencecritic_log_incoming", path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _valid_row(**overrides):
    row = {
        "provider": "fixture",
        "model": "fixture",
        "date": "2026-11-24T00:00:00Z",
        "query": "What is 2+2?",
        "draft": "2 + 2 = 4.",
        "retrieved_ids": [],
        "raw_critique": "{}",
        "critique": {
            "selection_filter": "Arithmetic identity",
            "visible_damage": [],
            "empty_regions": [],
            "non_survivors": [],
            "unknown_lethality": [],
            "survivorship_risk": 0.0,
            "confidence_adjustment": "unchanged",
            "caveats": [],
            "missing_categories": [],
            "suggested_queries": [],
        },
        "parse_error": None,
    }
    row.update(overrides)
    return row


def test_sample_incoming_row_validates():
    mod = _incoming_mod()
    line = (ROOT / "tests" / "fixtures" / "incoming_sample.jsonl").read_text(
        encoding="utf-8"
    ).strip()
    parsed = mod.parse_incoming_row(json.loads(line))
    assert parsed["query"] == "What is 2+2?"
    assert parsed["critique"] is not None
    assert parsed["parse_error"] is None


def test_incoming_rejects_missing_provider():
    mod = _incoming_mod()
    row = _valid_row()
    del row["provider"]
    with pytest.raises(ValueError, match="missing"):
        mod.parse_incoming_row(row)


def test_incoming_rejects_critique_and_parse_error():
    mod = _incoming_mod()
    with pytest.raises(ValueError, match="both"):
        mod.parse_incoming_row(_valid_row(parse_error="nope"))


def test_incoming_rejects_writing_gold_train(tmp_path: Path):
    mod = _incoming_mod()
    with pytest.raises(ValueError, match="cannot write gold"):
        mod.append_incoming(tmp_path / "train.jsonl", _valid_row())


def test_incoming_parse_error_without_critique():
    mod = _incoming_mod()
    parsed = mod.parse_incoming_row(
        _valid_row(critique=None, parse_error="Could not parse a JSON object")
    )
    assert parsed["critique"] is None
    assert "parse" in parsed["parse_error"].lower()


def test_capture_fixture_run_does_not_call_generate_with_store():
    mod = _incoming_mod()
    row = mod.capture_run(
        "What is 2+2?",
        provider=FixtureLLM(default_fixture_path()),
        store=YamlStore(default_store_dir()),
        provider_name="fixture",
    )
    assert row["provider"] == "fixture"
    assert row["draft"]
    assert row["critique"] is not None or row["parse_error"]
    assert "store_hits" not in row


def test_log_incoming_cli_writes_quarantine(tmp_path: Path):
    log = _log_mod()
    dest = tmp_path / "runs.jsonl"
    assert log.main(["--provider", "fixture", "--query", "What is 2+2?", "--out", str(dest)]) == 0
    lines = dest.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    row = json.loads(lines[0])
    assert row["query"] == "What is 2+2?"
    assert row["provider"] == "fixture"
