# Copyright 2026 Guzino (https://github.com/guzino)
# SPDX-License-Identifier: Apache-2.0

"""Reject replacement characters, BEL, and other git-summary corruption."""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

BINARY_SUFFIXES = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".ico",
    ".pdf",
    ".zip",
    ".gz",
    ".whl",
    ".pyc",
    ".pyd",
    ".dll",
    ".exe",
    ".woff",
    ".woff2",
}

# C0/C1 controls except tab, LF, CR. BEL (U+0007) is how PowerShell
# backtick-a shows up as a replacement glyph in GitHub PR summaries.
FORBIDDEN_CODEPOINTS = set(range(32)) - {9, 10, 13}
FORBIDDEN_CODEPOINTS.add(127)
FORBIDDEN_CODEPOINTS.update(range(0x80, 0xA0))

# UTF-8 decoded as Latin-1/CP1252, then saved as UTF-8 again.
MOJIBAKE_MARKERS = (
    "\ufffd",
    "\u00e2\u20ac",  # leading bytes of a mangled UTF-8 punctuation sequence
    "\u00c3\u00a9",  # e-acute double-encoded
)


def _tracked_files() -> list[Path]:
    raw = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT)
    return [ROOT / Path(name.decode()) for name in raw.split(b"\x00") if name]


def test_tracked_text_files_are_clean_utf8():
    failures: list[str] = []
    for path in _tracked_files():
        if path.suffix.lower() in BINARY_SUFFIXES:
            continue
        data = path.read_bytes()
        rel = path.relative_to(ROOT).as_posix()
        if data.startswith(b"\xef\xbb\xbf"):
            failures.append(f"{rel}: UTF-8 BOM")
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError as exc:
            failures.append(f"{rel}: not UTF-8 ({exc})")
            continue
        if "\ufffd" in text:
            failures.append(f"{rel}: U+FFFD replacement character")
        for i, char in enumerate(text):
            if ord(char) in FORBIDDEN_CODEPOINTS:
                failures.append(f"{rel}: control U+{ord(char):04X} at index {i}")
                break
        for marker in MOJIBAKE_MARKERS:
            if marker in text:
                failures.append(f"{rel}: mojibake marker {marker!r}")
                break
    assert not failures, "clean-text failures:\n" + "\n".join(failures)


def test_head_commit_message_has_no_control_chars():
    raw = subprocess.check_output(["git", "log", "-1", "--format=%B"], cwd=ROOT)
    text = raw.decode("utf-8")
    bad = [f"U+{ord(ch):04X}" for ch in text if ord(ch) in FORBIDDEN_CODEPOINTS]
    assert not bad, f"HEAD commit message has control characters: {bad}"
