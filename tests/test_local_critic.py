# Copyright 2026 Guzino (https://github.com/guzino)
# SPDX-License-Identifier: Apache-2.0

import json

from absencecritic.adapters.llm.fixture import FixtureLLM
from absencecritic.adapters.llm.local import LocalCritic
from absencecritic.adapters.llm.openai_compat import OpenAICompat
from absencecritic.adapters.store.yaml_store import YamlStore
from absencecritic.application.jsonutil import parse_json_object
from absencecritic.application.loop import run
from absencecritic.domain.models import Critique
from absencecritic.paths import default_fixture_path, default_store_dir

CONTROL = "What is 2+2?"


def _critique_json() -> str:
    return json.dumps(
        {
            "selection_filter": "Arithmetic identity; not filtered by publication or platform survival.",
            "visible_damage": [],
            "empty_regions": [],
            "non_survivors": [],
            "unknown_lethality": [],
            "survivorship_risk": 0.0,
            "confidence_adjustment": "unchanged",
            "caveats": [],
            "missing_categories": [],
            "suggested_queries": [],
        }
    )


class SpyGenerator:
    def __init__(self) -> None:
        self.generate_calls: list[dict] = []
        inner = FixtureLLM(default_fixture_path())
        self._inner = inner

    def generate(self, *, query: str) -> str:
        self.generate_calls.append({"query": query})
        return self._inner.generate(query=query)

    def revise(self, *, query: str, draft: str, critique_json: str) -> str:
        return self._inner.revise(
            query=query, draft=draft, critique_json=critique_json
        )


def test_local_critic_is_critic_port_only():
    critic = LocalCritic(api_key="local", base_url="http://127.0.0.1:9/v1")
    assert not hasattr(critic, "generate")
    assert not hasattr(critic, "revise")
    assert callable(critic.critique)


def test_local_critic_output_validates_as_critique(monkeypatch):
    payload = _critique_json()

    def fake_chat(self, system, user, *, temperature, json_object):
        del self, system, user, temperature
        assert json_object is True
        return payload

    monkeypatch.setattr(OpenAICompat, "_chat", fake_chat)
    critic = LocalCritic(api_key="local", base_url="http://127.0.0.1:9/v1")
    raw = critic.critique(query=CONTROL, draft="2 + 2 = 4.", store_hits="")
    Critique.model_validate(parse_json_object(raw))


def test_loop_with_local_critic_does_not_pass_store_to_generate(monkeypatch):
    payload = _critique_json()
    monkeypatch.setattr(OpenAICompat, "_chat", lambda *a, **k: payload)
    spy = SpyGenerator()
    result = run(
        CONTROL,
        generator=spy,
        critic=LocalCritic(api_key="local", base_url="http://127.0.0.1:9/v1"),
        store=YamlStore(default_store_dir()),
    )
    assert spy.generate_calls == [{"query": CONTROL}]
    assert result.critique is not None
    assert result.critique.confidence_adjustment.value == "unchanged"
