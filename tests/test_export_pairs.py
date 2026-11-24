# Copyright 2026 Guzino (https://github.com/guzino)
# SPDX-License-Identifier: Apache-2.0

import importlib.util
import json
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]


def _mod():
    path = ROOT / "eval" / "export_pairs.py"
    spec = importlib.util.spec_from_file_location("absencecritic_export_pairs", path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_strip_store_body_drops_summaries():
    mod = _mod()
    cleaned = mod.strip_store_body(
        {
            "non_survivors": [
                {
                    "id": "bls-establishment-survival",
                    "summary": "Many new establishments do not survive.",
                    "provenance": "BLS BED",
                    "confidence": 0.85,
                }
            ],
            "store_hits": "secret yaml body",
        }
    )
    assert "store_hits" not in cleaned
    assert "summary" not in cleaned["non_survivors"][0]
    assert cleaned["non_survivors"][0]["id"] == "bls-establishment-survival"


def test_make_pair_refuses_private_ids():
    mod = _mod()
    with pytest.raises(ValueError, match="private store"):
        mod.make_pair(
            query_id="startup-launch",
            query="What works for launching a startup?",
            rejected="just ship",
            chosen="caveat",
            critique={"non_survivors": []},
            retrieved_ids=["startup-user-note"],
            provider="fixture",
            model="fixture",
            private_ids={"startup-user-note"},
        )


def test_make_pair_allows_private_with_flag():
    mod = _mod()
    pair = mod.make_pair(
        query_id="startup-launch",
        query="What works for launching a startup?",
        rejected="just ship",
        chosen="caveat",
        critique={"non_survivors": [{"id": "x", "summary": "hide me"}]},
        retrieved_ids=["startup-user-note"],
        provider="fixture",
        model="fixture",
        private_ids={"startup-user-note"},
        allow_private=True,
    )
    assert "summary" not in pair["critique"]["non_survivors"][0]
    assert pair["chosen"] == "caveat"
    assert pair["rejected"] == "just ship"
    assert "license_note" in pair


def test_fixture_export_writes_pairs_without_store_summaries(tmp_path: Path):
    mod = _mod()
    queries = tmp_path / "queries.yaml"
    queries.write_text(
        yaml.safe_dump(
            {
                "queries": [
                    {
                        "id": "two-plus-two",
                        "kind": "control",
                        "query": "What is 2+2?",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    dest = tmp_path / "pairs.jsonl"
    assert (
        mod.main(
            [
                "--provider",
                "fixture",
                "--queries",
                str(queries),
                "--out",
                str(dest),
            ]
        )
        == 0
    )
    pair = json.loads(dest.read_text(encoding="utf-8").strip())
    assert pair["prompt"] == "What is 2+2?"
    assert pair["rejected"]
    assert pair["chosen"]
    assert pair["query_id"] == "two-plus-two"
    if pair.get("critique") and pair["critique"].get("non_survivors"):
        for hit in pair["critique"]["non_survivors"]:
            assert "summary" not in hit
