# Copyright 2026 Guzino (https://github.com/guzino)
# SPDX-License-Identifier: Apache-2.0

"""One command for a new clone: editable install + local Ollama."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    pip = [sys.executable, "-m", "pip", "install", "-e", f"{ROOT}[dev]"]
    print("+", " ".join(pip), flush=True)
    subprocess.run(pip, check=True)
    setup = [
        sys.executable,
        "-m",
        "absencecritic.adapters.cli.setup_ollama",
    ]
    print("+", " ".join(setup), flush=True)
    return subprocess.call(setup)


if __name__ == "__main__":
    raise SystemExit(main())
