# Copyright 2026 Guzino (https://github.com/guzino)
# SPDX-License-Identifier: Apache-2.0

import importlib.util
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
GOLD = ROOT / "eval" / "gold"


def _export_mod():
    path = ROOT / "eval" / "export_gold.py"
    spec = importlib.util.spec_from_file_location("absencecritic_export_gold", path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_gold_records_validate_and_match_committed_jsonl(tmp_path: Path):
    mod = _export_mod()
    rows = mod.gold_records()
    assert len(rows) >= 15
    kinds = {row["kind"] for row in rows}
    assert "biased" in kinds
    assert "control" in kinds
    assert all(row["id"] for row in rows)
    assert all(row["provenance"] == "eval/fixtures/responses.yaml" for row in rows)
    dest = tmp_path / "critiques.jsonl"
    written = mod.write_gold(dest)
    for name in ("critiques.jsonl", "train.jsonl", "heldout.jsonl"):
        assert (tmp_path / name).read_text(encoding="utf-8") == (
            GOLD / name
        ).read_text(encoding="utf-8")
    assert written == dest


def test_train_and_heldout_are_disjoint_and_cover_gold():
    mod = _export_mod()
    train_ids, heldout_ids = mod.load_splits()
    overlap = set(train_ids) & set(heldout_ids)
    assert not overlap
    gold_ids = {row["id"] for row in mod.gold_records()}
    assert set(train_ids) | set(heldout_ids) == gold_ids
    heldout_rows = [row for row in mod.gold_records() if row["id"] in set(heldout_ids)]
    heldout_kinds = {row["kind"] for row in heldout_rows}
    assert "biased" in heldout_kinds
    assert "control" in heldout_kinds


def test_overlapping_splits_fail(tmp_path: Path):
    mod = _export_mod()
    bad = tmp_path / "splits.yaml"
    bad.write_text(
        yaml.safe_dump({"train": ["startup-launch"], "heldout": ["startup-launch"]}),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="both train and heldout"):
        mod.load_splits(bad)
