# Copyright 2026 Guzino (https://github.com/guzino)
# SPDX-License-Identifier: Apache-2.0

import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "eval"))

from answer_checks import leaks_pipeline  # noqa: E402


@pytest.mark.parametrize(
    "text",
    [
        "The draft already states the core problem correctly: any claim fails.",
        "To keep it useful, here is a revised version:",
        "Any conclusion would be unreliable.\n\nNo non-survivor data retrieved; all failure cases unknown.",
        "Nothing relevant was retrieved from the store.",
        "The store hits do not cover this domain.",
        "Per the critique, confidence should drop.",
    ],
)
def test_pipeline_talk_is_flagged(text):
    assert leaks_pipeline(text)


@pytest.mark.parametrize(
    "text",
    [
        "Paris.",
        "Retrieval-augmented generation retrieves passages before answering.",
        "Caveat: cities where crime did not fall are missing from this sample.",
        "Draft a budget and stick to it.",
        "Data retrieved from BLS tables show half of new firms close by year five.",
    ],
)
def test_normal_answers_pass(text):
    assert not leaks_pipeline(text)


def test_recorded_fixture_answers_do_not_leak():
    fixtures = yaml.safe_load(
        (ROOT / "eval" / "fixtures" / "responses.yaml").read_text(encoding="utf-8")
    )
    for item in fixtures:
        assert not leaks_pipeline(item["revision"]), item["query"]


def test_benchmark_score_fails_a_leaking_answer():
    sys.path.insert(0, str(ROOT / "eval" / "benchmark"))
    from score import score_answer

    item = {
        "id": "x",
        "kind": "biased",
        "labels": {
            "should_caveate": True,
            "should_not_abstain": True,
            "must_mention_missing_data": True,
        },
    }
    clean = score_answer(item, "Failed shops are missing from this sample.")
    leaked = score_answer(item, "The draft is fine. Failed shops are missing from this sample.")
    assert clean["pass"] and not clean["pipeline_leak"]
    assert not leaked["pass"] and leaked["pipeline_leak"]
