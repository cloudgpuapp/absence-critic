# Copyright 2026 Guzino (https://github.com/guzino)
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path

from absencecritic.adapters.llm.openai_compat import OpenAICompat
from absencecritic.envfile import parse_env_file


def test_parse_env_file(tmp_path: Path):
    path = tmp_path / ".env"
    path.write_text("ABSENCECRITIC_PROVIDER=ollama\nOPENAI_API_KEY=ollama\n", encoding="utf-8")
    parsed = parse_env_file(path)
    assert parsed["ABSENCECRITIC_PROVIDER"] == "ollama"


def test_ollama_factory_does_not_need_cloud_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_BASE_URL", raising=False)
    monkeypatch.delenv("ABSENCECRITIC_MODEL", raising=False)
    llm = OpenAICompat.ollama()
    assert llm.api_key == "ollama"
    assert "11434" in llm.base_url
    assert llm.model == "qwen2.5:3b"
