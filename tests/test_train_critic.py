# Copyright 2026 Guzino (https://github.com/guzino)
# SPDX-License-Identifier: Apache-2.0

import importlib.util
import json
from pathlib import Path

import pytest

from absencecritic.domain.models import Critique

ROOT = Path(__file__).resolve().parents[1]


def _mod():
    path = ROOT / "scripts" / "train_critic.py"
    spec = importlib.util.spec_from_file_location("absencecritic_train_critic", path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_dry_run_accepts_committed_train_jsonl():
    mod = _mod()
    assert mod.main(["--dry-run"]) == 0
    rows = mod.load_train_rows(ROOT / "eval" / "gold" / "train.jsonl")
    assert len(rows) >= 1
    for row in rows:
        Critique.model_validate(row["critique"])


def test_dry_run_rejects_invalid_json(tmp_path: Path):
    mod = _mod()
    bad = tmp_path / "train.jsonl"
    bad.write_text("{not json\n", encoding="utf-8")
    with pytest.raises(ValueError, match="invalid JSON"):
        mod.load_train_rows(bad)


def test_refuses_heldout_as_train(tmp_path: Path):
    mod = _mod()
    path = tmp_path / "heldout.jsonl"
    path.write_text("{}\n", encoding="utf-8")
    with pytest.raises(ValueError, match="refusing heldout.jsonl"):
        mod.load_train_rows(path)


def test_export_chat_is_critic_not_generator(tmp_path: Path):
    mod = _mod()
    dest = tmp_path / "critic_sft.jsonl"
    assert mod.main(["--export-chat", str(dest)]) == 0
    row = json.loads(dest.read_text(encoding="utf-8").splitlines()[0])
    roles = [m["role"] for m in row["messages"]]
    assert roles == ["system", "user", "assistant"]
    assistant = json.loads(row["messages"][2]["content"])
    Critique.model_validate(assistant)
    user = row["messages"][1]["content"]
    assert "Draft answer" in user
    assert "did not see the Non-Survivor Store" in user
