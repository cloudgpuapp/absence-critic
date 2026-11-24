# Copyright 2026 Guzino (https://github.com/guzino)
# SPDX-License-Identifier: Apache-2.0

import pytest
from pydantic import ValidationError

from absencecritic.domain.models import Critique, StoreEntry


def test_critique_accepts_valid_payload():
    c = Critique(
        selection_filter="publication",
        survivorship_risk=0.4,
        confidence_adjustment="lower",
    )
    assert c.caveats == []
    assert c.confidence_adjustment.value == "lower"


def test_critique_rejects_bad_risk():
    with pytest.raises(ValidationError):
        Critique(
            selection_filter="x",
            survivorship_risk=1.5,
            confidence_adjustment="unchanged",
        )


def test_store_entry_roundtrip():
    e = StoreEntry(
        id="x",
        domain="startups",
        selection_process="s",
        survivor_pattern="p",
        non_survivor_evidence="e",
        confidence=0.5,
        provenance="author prior, low confidence",
        collection="catalog",
        source_url="https://example.org/note",
        ingested_at="2026-11-24T16:00:00+00:00",
    )
    again = StoreEntry.model_validate(e.model_dump())
    assert again.id == "x"
    assert again.collection.value == "catalog"
    assert again.source_url == "https://example.org/note"
    assert again.ingested_at == "2026-11-24T16:00:00+00:00"


def test_store_entry_defaults_collection_seed_when_omitted():
    e = StoreEntry(
        id="legacy",
        domain="startups",
        selection_process="s",
        survivor_pattern="p",
        non_survivor_evidence="e",
        confidence=0.5,
        provenance="test",
    )
    assert e.collection.value == "seed"
    assert e.source_url is None
    assert e.ingested_at is None


def test_store_entry_rejects_unknown_collection():
    with pytest.raises(ValidationError):
        StoreEntry(
            id="x",
            domain="startups",
            selection_process="s",
            survivor_pattern="p",
            non_survivor_evidence="e",
            confidence=0.5,
            provenance="test",
            collection="scraped",
        )
