# Copyright 2026 Guzino (https://github.com/guzino)
# SPDX-License-Identifier: Apache-2.0

import importlib.util
from pathlib import Path


def test_fixture_eval_passes():
    eval_path = Path(__file__).resolve().parents[1] / "eval" / "run_eval.py"
    spec = importlib.util.spec_from_file_location("absencecritic_eval", eval_path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert mod.main(["--provider", "fixture"]) == 0
