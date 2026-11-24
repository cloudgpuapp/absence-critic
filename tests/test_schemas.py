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
    )
    assert StoreEntry.model_validate(e.model_dump()).id == "x"
