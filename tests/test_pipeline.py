# Copyright 2026 Guzino (https://github.com/guzino)
# SPDX-License-Identifier: Apache-2.0

from absencecritic import run
from absencecritic.adapters.llm.fixture import FixtureLLM
from absencecritic.adapters.store.yaml_store import YamlStore
from absencecritic.paths import default_fixture_path, default_store_dir


def _run(query: str, *, shield: bool = True):
    return run(
        query,
        provider=FixtureLLM(default_fixture_path()),
        store=YamlStore(default_store_dir()),
        shield=shield,
    )


def test_baseline_skips_critic():
    q = "What is 2+2?"
    result = _run(q, shield=False)
    assert result.shielded is False
    assert result.critique is None
    assert result.final == result.draft
    assert result.retrieved_ids == []


def test_shielded_startup_uses_store_and_lowers_confidence():
    result = _run("What works for launching a startup?")
    assert result.critique is not None
    assert result.critique.confidence_adjustment.value in {
        "lower",
        "seek_more_data",
        "abstain",
    }
    assert "bls-establishment-survival" in result.retrieved_ids or result.retrieved_ids
    used = {h.id for h in result.critique.non_survivors}
    assert used
    assert "surviv" in result.final.lower() or "missing" in result.final.lower() or "base" in result.final.lower()


def test_control_does_not_abstain():
    result = _run("What is 2+2?")
    assert result.critique is not None
    assert result.critique.confidence_adjustment.value == "unchanged"
    assert result.critique.survivorship_risk < 0.5
    assert result.retrieved_ids == []
    assert result.final.strip().endswith("4.") or "4" in result.final


def test_plan_like_launch_query_still_caveats():
    result = _run("How should I plan a product launch that is guaranteed to succeed?")
    assert result.critique is not None
    assert result.critique.confidence_adjustment.value in {
        "lower",
        "seek_more_data",
        "abstain",
    }
    assert result.critique.empty_regions
    assert "missing" in result.final.lower() or "cannot" in result.final.lower()


def test_wald_quote_skips_store_retrieve():
    result = _run("Quote Abraham Wald's survivorship-bias insight in one sentence.")
    assert result.retrieved_ids == []
