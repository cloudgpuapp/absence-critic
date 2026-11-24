# Copyright 2026 Guzino (https://github.com/guzino)
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path

import pytest

from absencecritic.adapters.store.yaml_store import YamlStore, tokenize
from absencecritic.domain.models import StoreEntry
from absencecritic.paths import default_store_dir


def test_tokenize_drops_stopwords():
    assert "the" not in tokenize("the startup failed")
    assert "startup" in tokenize("the startup failed")


def test_retrieve_ranks_startup_above_unrelated(tmp_path: Path):
    (tmp_path / "a.yaml").write_text(
        """
- id: startup-fail
  domain: startups
  selection_process: funded founders write advice
  survivor_pattern: success posts
  non_survivor_evidence: most attempts close quietly
  confidence: 0.8
  provenance: test
- id: boiling
  domain: physics
  selection_process: none
  survivor_pattern: constants
  non_survivor_evidence: n/a
  confidence: 0.1
  provenance: test
""",
        encoding="utf-8",
    )
    store = YamlStore(tmp_path)
    hits = store.retrieve("What works for launching a startup?")
    assert hits
    assert hits[0][0].id == "startup-fail"


def test_seeded_store_loads():
    store = YamlStore(default_store_dir())
    assert len(store.entries) >= 20
    ids = {e.id for e in store.entries}
    assert "bls-establishment-survival" in ids
    bls = next(e for e in store.entries if e.id == "bls-establishment-survival")
    assert bls.collection.value == "seed"


def test_add_stamps_ingested_at_and_roundtrips_collection(tmp_path: Path):
    store = YamlStore(tmp_path)
    store.add(
        StoreEntry(
            id="startup-cohort-note",
            domain="startups",
            selection_process="public advice is written by firms that lasted",
            survivor_pattern="visible launch playbooks",
            non_survivor_evidence="quiet closures are missing from blogs",
            confidence=0.6,
            provenance="Author prior, low confidence",
            collection="catalog",
            source_url="https://example.org/bed",
        )
    )
    text = (tmp_path / "ingested.yaml").read_text(encoding="utf-8")
    assert "schema_version: 1" in text
    loaded = YamlStore(tmp_path).entries[0]
    assert loaded.collection.value == "catalog"
    assert loaded.source_url == "https://example.org/bed"
    assert loaded.ingested_at
    assert "T" in loaded.ingested_at


def test_add_appends_ingested_yaml_and_ranks(tmp_path: Path):
    store = YamlStore(tmp_path)
    entry = StoreEntry(
        id="startup-silent-shutdown",
        domain="startups",
        selection_process="public advice is written by firms that lasted",
        survivor_pattern="visible launch playbooks",
        non_survivor_evidence="cohorts that close without a post-mortem are missing from blogs",
        confidence=0.7,
        provenance="Author prior, low confidence",
    )
    store.add(entry)
    assert (tmp_path / "ingested.yaml").exists()
    reloaded = YamlStore(tmp_path)
    assert any(e.id == "startup-silent-shutdown" for e in reloaded.entries)
    hits = reloaded.retrieve("What works for launching a startup?")
    assert hits
    assert hits[0][0].id == "startup-silent-shutdown"


def test_add_rejects_duplicate_id(tmp_path: Path):
    (tmp_path / "seed.yaml").write_text(
        """
- id: already
  domain: startups
  selection_process: filter
  survivor_pattern: survivors
  non_survivor_evidence: missing attempts
  confidence: 0.5
  provenance: test
""",
        encoding="utf-8",
    )
    store = YamlStore(tmp_path)
    with pytest.raises(ValueError, match="duplicate store id"):
        store.add(
            StoreEntry(
                id="already",
                domain="startups",
                selection_process="filter",
                survivor_pattern="survivors",
                non_survivor_evidence="missing attempts",
                confidence=0.5,
                provenance="test",
            )
        )
