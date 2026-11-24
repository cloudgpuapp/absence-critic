# Copyright 2026 Guzino (https://github.com/guzino)
# SPDX-License-Identifier: Apache-2.0

from absencecritic.application.retrieve import suggested_retrieve_k


def test_controls_fetch_nothing():
    assert suggested_retrieve_k("What is 2+2?") == 0
    assert suggested_retrieve_k("What is the boiling point of water at standard pressure?") == 0
    assert suggested_retrieve_k(
        "Quote Abraham Wald's survivorship-bias insight in one sentence."
    ) == 0


def test_survivor_advice_fetches_high():
    assert suggested_retrieve_k("What works for launching a startup?") == 5
    assert suggested_retrieve_k(
        "How should I plan a product launch that is guaranteed to succeed?"
    ) == 5
    assert suggested_retrieve_k("What career advice actually works based on LinkedIn stories?") == 5


def test_unknown_query_fetches_one():
    assert suggested_retrieve_k("Explain photosynthesis in two sentences.") == 1
