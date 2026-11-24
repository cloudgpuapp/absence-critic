# Copyright 2026 Guzino (https://github.com/guzino)
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path

from absencecritic.envfile import parse_env_file


def test_parse_env_file(tmp_path: Path):
    path = tmp_path / ".env"
    path.write_text("OPENAI_API_KEY=sk-test\n# comment\n\n", encoding="utf-8")
    parsed = parse_env_file(path)
    assert parsed["OPENAI_API_KEY"] == "sk-test"
    assert "comment" not in parsed
