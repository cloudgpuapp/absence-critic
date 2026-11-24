# Copyright 2026 Guzino (https://github.com/guzino)
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path

import yaml

from absencecritic.adapters.store.yaml_store import YamlStore
from absencecritic.application.retrieve import suggested_retrieve_k
from absencecritic.paths import default_store_dir

ROOT = Path(__file__).resolve().parents[1]


def test_controls_fetch_nothing():
    assert suggested_retrieve_k("Compute 7+8.") == 0
    assert suggested_retrieve_k("What is the boiling point of ethanol?") == 0
    assert suggested_retrieve_k("Quote the survivorship-bias insight in one sentence.") == 0
    assert suggested_retrieve_k("What is the chemical formula for table salt?") == 0


def test_survivor_advice_fetches_high():
    assert suggested_retrieve_k("If I copy visible playbooks, what actually works?") == 5
    assert suggested_retrieve_k(
        "How should I schedule a release that is guaranteed to succeed?"
    ) == 5
    assert suggested_retrieve_k(
        "What career advice actually works if I only read polished success stories?"
    ) == 5
    assert suggested_retrieve_k(
        "Should we staff a vacancy using only people still on payroll after ten years?"
    ) == 5


def test_unknown_query_fetches_one():
    assert suggested_retrieve_k("Explain photosynthesis in two sentences.") == 1


def test_paraphrases_match_k_and_overlap_store_hits():
    originals = {
        item["id"]: item["query"]
        for item in yaml.safe_load((ROOT / "eval" / "queries.yaml").read_text(encoding="utf-8"))[
            "queries"
        ]
    }
    paraphrases = {
        item["id"]: item["query"]
        for item in yaml.safe_load(
            (ROOT / "eval" / "queries_paraphrase.yaml").read_text(encoding="utf-8")
        )["paraphrases"]
    }
    assert set(originals) == set(paraphrases)
    store = YamlStore(default_store_dir())
    for qid, query in originals.items():
        other = paraphrases[qid]
        assert suggested_retrieve_k(query) == suggested_retrieve_k(other), qid
        left_hits = store.retrieve(query, k=5)
        right_hits = store.retrieve(other, k=5)
        left = {entry.id for entry, _ in left_hits}
        right = {entry.id for entry, _ in right_hits}
        if suggested_retrieve_k(query) == 0:
            assert left == set() and right == set(), qid
            continue
        if not left and not right:
            continue
        left_dom = {entry.domain for entry, _ in left_hits}
        right_dom = {entry.domain for entry, _ in right_hits}
        assert left & right or left_dom & right_dom, qid
