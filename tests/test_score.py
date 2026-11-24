# Copyright 2026 Guzino (https://github.com/guzino)
# SPDX-License-Identifier: Apache-2.0

import inspect

from absencecritic import score
from absencecritic.adapters.llm.fixture import FixtureLLM
from absencecritic.adapters.store.yaml_store import YamlStore
from absencecritic.paths import default_fixture_path, default_store_dir


def test_score_signature_has_no_generator():
    assert "generator" not in inspect.signature(score).parameters


def test_score_does_not_call_generate_or_revise():
    result = score(
        "What is 2+2?",
        "2 + 2 = 4.",
        critic=FixtureLLM(default_fixture_path()),
        store=YamlStore(default_store_dir()),
    )
    assert result.final == ""
    assert result.draft == "2 + 2 = 4."
    assert result.critique is not None
    assert result.critique.survivorship_risk < 0.5
    assert result.critique.confidence_adjustment.value == "unchanged"


def test_score_control_draft_stays_low_risk():
    result = score(
        "What is 2+2?",
        "Absolutely guaranteed: 2+2 is 4 because every blog said so.",
        critic=FixtureLLM(default_fixture_path()),
        store=YamlStore(default_store_dir()),
    )
    assert result.critique is not None
    assert result.critique.survivorship_risk < 0.5


def test_score_biased_draft_still_high_risk():
    result = score(
        "What works for launching a startup?",
        "Copy the last unicorn. Guaranteed success.",
        critic=FixtureLLM(default_fixture_path()),
        store=YamlStore(default_store_dir()),
    )
    assert result.critique is not None
    assert result.critique.confidence_adjustment.value in {
        "lower",
        "seek_more_data",
        "abstain",
    }
    assert result.final == ""
