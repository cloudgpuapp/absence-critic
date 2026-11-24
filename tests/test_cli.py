# Copyright 2026 Guzino (https://github.com/guzino)
# SPDX-License-Identifier: Apache-2.0

import json

from absencecritic.cli import main


def test_cli_json_shielded(capsys):
    code = main(
        [
            "--provider",
            "fixture",
            "--json",
            "--show-critique",
            "What is 2+2?",
        ]
    )
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["shielded"] is True
    assert payload["critique"]["confidence_adjustment"] == "unchanged"


def test_cli_no_shield(capsys):
    code = main(["--provider", "fixture", "--no-shield", "--json", "What is 2+2?"])
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["shielded"] is False
    assert payload["critique"] is None
