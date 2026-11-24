# Copyright 2026 Guzino (https://github.com/guzino)
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path

import pytest

from absencecritic.adapters.store.feedback import (
    MAX_FEEDBACK_CONFIDENCE,
    UNVERIFIED,
    accept_feedback,
    queue_feedback,
)
from absencecritic.adapters.store.yaml_store import YamlStore
from absencecritic.cli import main
from absencecritic.domain.models import StoreCollection, StoreStatus


def _note(path: Path, *, confidence: float = 0.9, provenance: str = "alice 2026-11-24") -> None:
    path.write_text(
        f"""
- id: startup-user-note
  domain: startups
  selection_process: local team saw quiet shutdowns that never hit blogs
  survivor_pattern: public launch playbooks
  non_survivor_evidence: one cohort closed without a post-mortem
  confidence: {confidence}
  provenance: {provenance}
""",
        encoding="utf-8",
    )


def test_pending_feedback_does_not_retrieve(tmp_path: Path):
    store_dir = tmp_path / "store"
    store_dir.mkdir()
    note = tmp_path / "note.yaml"
    _note(note)
    ids = queue_feedback(store_dir, note)
    assert ids == ["startup-user-note"]
    store = YamlStore(store_dir)
    pending = next(e for e in store.entries if e.id == "startup-user-note")
    assert pending.collection is StoreCollection.feedback
    assert pending.status is StoreStatus.pending
    assert pending.confidence <= MAX_FEEDBACK_CONFIDENCE
    assert UNVERIFIED in pending.provenance.lower()
    hits = store.retrieve("What works for launching a startup?")
    assert all(h[0].id != "startup-user-note" for h in hits)


def test_accepted_feedback_can_retrieve(tmp_path: Path):
    store_dir = tmp_path / "store"
    store_dir.mkdir()
    note = tmp_path / "note.yaml"
    _note(note)
    queue_feedback(store_dir, note)
    accept_feedback(store_dir, "startup-user-note")
    hits = YamlStore(store_dir).retrieve("What works for launching a startup?")
    assert hits
    assert hits[0][0].id == "startup-user-note"
    assert hits[0][0].status is StoreStatus.accepted


def test_feedback_requires_provenance(tmp_path: Path):
    store_dir = tmp_path / "store"
    store_dir.mkdir()
    note = tmp_path / "note.yaml"
    _note(note, provenance="   ")
    with pytest.raises(ValueError, match="provenance"):
        queue_feedback(store_dir, note)


def test_cli_feedback_queue_and_accept(tmp_path, capsys):
    note = tmp_path / "note.yaml"
    _note(note)
    store_dir = tmp_path / "store"
    store_dir.mkdir()
    assert main(["feedback", str(note), "--store", str(store_dir)]) == 0
    assert "startup-user-note" in capsys.readouterr().out
    assert main(
        ["feedback", "--accept", "startup-user-note", "--store", str(store_dir)]
    ) == 0
    hits = YamlStore(store_dir).retrieve("What works for launching a startup?")
    assert any(h[0].id == "startup-user-note" for h in hits)
