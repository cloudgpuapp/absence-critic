# Copyright 2026 Guzino (https://github.com/guzino)
# SPDX-License-Identifier: Apache-2.0

import importlib.util
from pathlib import Path

from absencecritic.adapters.store.feedback import accept_feedback, queue_feedback
from absencecritic.adapters.store.yaml_store import YamlStore


def _entry_yaml(entry_id: str) -> str:
    return f"""
- id: {entry_id}
  domain: startups
  selection_process: local cohort
  survivor_pattern: public playbooks
  non_survivor_evidence: quiet shutdowns without a write-up
  confidence: 0.3
  provenance: test fixture, not independently verified
"""


def _pairs_mod():
    path = Path(__file__).resolve().parents[1] / "eval" / "export_pairs.py"
    spec = importlib.util.spec_from_file_location("absencecritic_export_pairs_org", path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_nested_private_folder_is_not_retrieved(tmp_path: Path):
    store_dir = tmp_path / "store"
    store_dir.mkdir()
    (store_dir / "seed.yaml").write_text(_entry_yaml("public-seed"), encoding="utf-8")
    hidden = store_dir / "private"
    hidden.mkdir()
    (hidden / "secret.yaml").write_text(_entry_yaml("org-secret"), encoding="utf-8")
    store = YamlStore(store_dir)
    ids = {entry.id for entry in store.entries}
    assert "public-seed" in ids
    assert "org-secret" not in ids
    hits = store.retrieve("What works for launching a startup?")
    assert all(entry.id != "org-secret" for entry, _ in hits)


def test_separate_org_store_dir_is_loaded(tmp_path: Path):
    org = tmp_path / "org-store"
    org.mkdir()
    (org / "entries.yaml").write_text(_entry_yaml("org-note"), encoding="utf-8")
    store = YamlStore(org)
    assert any(entry.id == "org-note" for entry in store.entries)


def test_feedback_ids_are_private_for_pair_export(tmp_path: Path):
    store_dir = tmp_path / "store"
    store_dir.mkdir()
    (store_dir / "seed.yaml").write_text(_entry_yaml("public-seed"), encoding="utf-8")
    note = tmp_path / "note.yaml"
    note.write_text(_entry_yaml("startup-user-note"), encoding="utf-8")
    queue_feedback(store_dir, note)
    accept_feedback(store_dir, "startup-user-note")
    store = YamlStore(store_dir)
    private_ids = _pairs_mod().private_entry_ids(store)
    assert "startup-user-note" in private_ids
    assert "public-seed" not in private_ids
