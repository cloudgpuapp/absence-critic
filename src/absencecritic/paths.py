# Copyright 2026 Guzino (https://github.com/guzino)
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import os
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def default_store_dir() -> Path:
    env = os.environ.get("ABSENCECRITIC_STORE")
    if env:
        return Path(env)
    return repo_root() / "data" / "non_survivors"


def default_fixture_path() -> Path:
    env = os.environ.get("ABSENCECRITIC_FIXTURES")
    if env:
        return Path(env)
    return repo_root() / "eval" / "fixtures" / "responses.yaml"
