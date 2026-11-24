# Copyright 2026 Guzino (https://github.com/guzino)
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path

import pytest

from absencecritic.adapters.store.catalog import ingest_catalog, load_catalog
from absencecritic.adapters.store.yaml_store import YamlStore
from absencecritic.domain.models import StoreCollection

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "catalog.yaml"


def test_fixture_catalog_loads_three_citable_rows():
    entries = load_catalog(FIXTURE)
    assert {e.id for e in entries} == {
        "catalog-bls-startup-survival",
        "catalog-osc-2015-replication",
        "catalog-franco-2014-nulls",
    }
    assert all(e.collection is StoreCollection.catalog for e in entries)
    assert all(e.source_url and e.source_url.startswith("https://") for e in entries)


def test_ingest_catalog_ranks_bls_row(tmp_path: Path):
    ids = ingest_catalog(tmp_path, FIXTURE)
    assert "catalog-bls-startup-survival" in ids
    hits = YamlStore(tmp_path).retrieve("What works for launching a startup?")
    assert hits
    assert hits[0][0].id == "catalog-bls-startup-survival"
    assert hits[0][0].collection is StoreCollection.catalog


def test_catalog_rejects_missing_source_url(tmp_path: Path):
    path = tmp_path / "bad.yaml"
    path.write_text(
        """
catalog:
  - id: no-url
    domain: startups
    collection: catalog
    source_url: ""
    selection_process: filter
    survivor_pattern: survivors
    non_survivor_evidence: missing
    confidence: 0.5
    provenance: a paper
""",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="source_url"):
        load_catalog(path)


def test_catalog_rejects_seed_collection(tmp_path: Path):
    path = tmp_path / "seedish.yaml"
    path.write_text(
        """
catalog:
  - id: wrong-pile
    domain: startups
    collection: seed
    source_url: https://www.bls.gov/bdm/
    selection_process: filter
    survivor_pattern: survivors
    non_survivor_evidence: missing
    confidence: 0.5
    provenance: BLS
""",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="collection=catalog"):
        load_catalog(path)
