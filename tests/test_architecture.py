# Copyright 2026 Guzino (https://github.com/guzino)
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "src" / "absencecritic"


def _imports(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.append(node.module)
    return names


def test_domain_does_not_import_application_or_adapters():
    for path in (ROOT / "domain").rglob("*.py"):
        for name in _imports(path):
            assert not name.startswith("absencecritic.application")
            assert not name.startswith("absencecritic.adapters")


def test_application_does_not_import_adapters():
    for path in (ROOT / "application").rglob("*.py"):
        for name in _imports(path):
            assert not name.startswith("absencecritic.adapters")
