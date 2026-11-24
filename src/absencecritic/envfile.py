# Copyright 2026 Guzino (https://github.com/guzino)
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from pathlib import Path

from absencecritic.paths import repo_root


def parse_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.is_file():
        return values
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            values[key] = value
    return values


def load_repo_env(*, override: bool = False) -> Path:
    """Load repo-root .env into os.environ. Existing vars win unless override."""
    import os

    path = repo_root() / ".env"
    for key, value in parse_env_file(path).items():
        if override or key not in os.environ:
            os.environ[key] = value
    return path
