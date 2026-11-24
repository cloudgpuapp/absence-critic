# Copyright 2026 Guzino (https://github.com/guzino)
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path

from absencecritic.adapters.store.yaml_store import YamlStore, tokenize
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
