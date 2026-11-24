# Copyright 2026 Guzino (https://github.com/guzino)
# SPDX-License-Identifier: Apache-2.0

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


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
    assert all(row["provenance"] == "eval/fixtures/responses.yaml" for row in rows)
    dest = tmp_path / "critiques.jsonl"
    written = mod.write_gold(dest)
    committed = (ROOT / "eval" / "gold" / "critiques.jsonl").read_text(encoding="utf-8")
    assert written.read_text(encoding="utf-8") == committed
