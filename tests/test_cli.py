# Copyright 2026 Guzino (https://github.com/guzino)
# SPDX-License-Identifier: Apache-2.0

import json
from pathlib import Path

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


def test_cli_ingest(tmp_path, capsys):
    source = tmp_path / "new.yaml"
    store_dir = tmp_path / "store"
    store_dir.mkdir()
    (store_dir / "seed.yaml").write_text(
        """
- id: seed
  domain: physics
  selection_process: none
  survivor_pattern: constants
  non_survivor_evidence: n/a
  confidence: 0.1
  provenance: test
""",
        encoding="utf-8",
    )
    source.write_text(
        """
- id: file-drawer-note
  domain: scientific_literature
  selection_process: journals prefer positive results
  survivor_pattern: published significant findings
  non_survivor_evidence: unpublished nulls are missing from the visible literature
  confidence: 0.8
  provenance: Author prior, low confidence
""",
        encoding="utf-8",
    )
    code = main(["ingest", str(source), "--store", str(store_dir)])
    assert code == 0
    assert "file-drawer-note" in capsys.readouterr().out
    assert (store_dir / "ingested.yaml").exists()


def test_cli_ingest_catalog(tmp_path, capsys):
    fixture = Path(__file__).resolve().parent / "fixtures" / "catalog.yaml"
    store_dir = tmp_path / "store"
    store_dir.mkdir()
    code = main(["ingest", "--catalog", str(fixture), "--store", str(store_dir)])
    assert code == 0
    out = capsys.readouterr().out
    assert "catalog-bls-startup-survival" in out
    assert (store_dir / "ingested.yaml").exists()


def test_cli_no_shield(capsys):
    code = main(["--provider", "fixture", "--no-shield", "--json", "What is 2+2?"])
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["shielded"] is False
    assert payload["critique"] is None
