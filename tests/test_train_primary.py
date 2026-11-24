# Copyright 2026 Guzino (https://github.com/guzino)
# SPDX-License-Identifier: Apache-2.0

import importlib.util
import json
from pathlib import Path

import pytest

from absencecritic.adapters.cli.main import _default_provider_name

ROOT = Path(__file__).resolve().parents[1]


def _mod():
    path = ROOT / "scripts" / "train_primary.py"
    spec = importlib.util.spec_from_file_location("absencecritic_train_primary", path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_dry_run_accepts_pair_schema(tmp_path: Path):
    mod = _mod()
    path = tmp_path / "pairs.jsonl"
    path.write_text(
        json.dumps(
            {
                "prompt": "What is 2+2?",
                "rejected": "2 + 2 = 4.",
                "chosen": "2 + 2 = 4.",
                "query_id": "two-plus-two",
                "critique": {"confidence_adjustment": "unchanged"},
            }
        )
        + "\n",
        encoding="utf-8",
    )
    assert mod.main(["--pairs", str(path), "--dry-run"]) == 0


def test_rejects_invalid_json(tmp_path: Path):
    mod = _mod()
    path = tmp_path / "pairs.jsonl"
    path.write_text("{not json\n", encoding="utf-8")
    with pytest.raises(ValueError, match="invalid JSON"):
        mod.load_pair_rows(path)


def test_rejects_critic_sft_chat_rows(tmp_path: Path):
    mod = _mod()
    path = tmp_path / "pairs.jsonl"
    path.write_text(
        json.dumps({"messages": [{"role": "system", "content": "critic"}]}) + "\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="critic SFT"):
        mod.load_pair_rows(path)


def test_rejects_store_body_in_critique(tmp_path: Path):
    mod = _mod()
    path = tmp_path / "pairs.jsonl"
    path.write_text(
        json.dumps(
            {
                "prompt": "q",
                "rejected": "a",
                "chosen": "b",
                "critique": {"non_survivors": [{"id": "x", "summary": "secret"}]},
            }
        )
        + "\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="store body"):
        mod.load_pair_rows(path)


def test_default_cli_provider_is_not_a_preference_checkpoint():
    assert _default_provider_name() in {"fixture", "openai"}
