# Copyright 2026 Guzino (https://github.com/guzino)
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

from absencecritic.domain.models import StoreEntry

INGEST_FILENAME = "ingested.yaml"
_INGEST_HEADER = """\
# Copyright 2026 Guzino (https://github.com/guzino)
# SPDX-License-Identifier: Apache-2.0
#
# Curated Phase 1 ingest. Written by YamlStore.add; seed notes stay in
# other YAML files in this directory.
"""

_TOKEN = re.compile(r"[a-z0-9]+")
_STOP = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "how",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "this",
    "to",
    "what",
    "with",
}


def _write_entries(path: Path, entries: list[StoreEntry]) -> None:
    payload = [
        e.model_dump(mode="json", exclude={"source_path"}, exclude_none=True)
        for e in entries
    ]
    body = yaml.safe_dump(payload, sort_keys=False, allow_unicode=True)
    path.write_text(_INGEST_HEADER + "\n" + body, encoding="utf-8")


def tokenize(text: str) -> set[str]:
    return {t for t in _TOKEN.findall(text.lower()) if t not in _STOP and len(t) > 1}


def load_entries(path: Path) -> list[StoreEntry]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in {".yaml", ".yml"}:
        raw = yaml.safe_load(text)
    elif path.suffix.lower() == ".jsonl":
        raw = [json.loads(line) for line in text.splitlines() if line.strip()]
    elif path.suffix.lower() == ".json":
        raw = json.loads(text)
    else:
        return []
    if raw is None:
        return []
    if isinstance(raw, dict):
        raw = raw.get("entries", [raw])
    if not isinstance(raw, list):
        raise ValueError(f"Expected a list of entries in {path}")
    entries = []
    for item in raw:
        entry = StoreEntry.model_validate(item)
        entry.source_path = str(path)
        entries.append(entry)
    return entries


class YamlStore:
    def __init__(self, directory: Path):
        self.directory = Path(directory)
        self.entries: list[StoreEntry] = []
        self._bags: list[set[str]] = []
        self.reload()

    def reload(self) -> None:
        self.entries = []
        if not self.directory.exists():
            raise FileNotFoundError(f"Non-Survivor Store not found: {self.directory}")
        files = sorted(
            p
            for p in self.directory.iterdir()
            if p.suffix.lower() in {".yaml", ".yml", ".json", ".jsonl"}
        )
        for path in files:
            self.entries.extend(load_entries(path))
        self._bags = [
            tokenize(
                " ".join(
                    [
                        e.id,
                        e.domain,
                        e.selection_process,
                        e.survivor_pattern,
                        e.non_survivor_evidence,
                        e.provenance,
                    ]
                )
            )
            for e in self.entries
        ]

    def retrieve(self, query: str, draft: str = "", k: int = 5) -> list[tuple[StoreEntry, float]]:
        q = tokenize(f"{query} {draft}")
        if not q:
            return []
        scored: list[tuple[int, float]] = []
        for i, bag in enumerate(self._bags):
            overlap = q & bag
            if not overlap:
                continue
            score = len(overlap) / len(q)
            domain = self.entries[i].domain.replace("_", " ")
            if domain in query.lower() or domain.replace(" ", "") in tokenize(query):
                score += 0.15
            if tokenize(self.entries[i].id) & q:
                score += 0.05
            scored.append((i, score))
        scored.sort(key=lambda item: item[1], reverse=True)
        return [(self.entries[i], score) for i, score in scored[:k]]

    def add(self, entry: StoreEntry) -> StoreEntry:
        """Append a validated entry to ingested.yaml. Retrieve-only StorePort is unchanged."""
        validated = StoreEntry.model_validate(
            entry.model_dump(exclude={"source_path"}, exclude_none=True)
        )
        if not validated.provenance.strip():
            raise ValueError("provenance is required")
        if any(existing.id == validated.id for existing in self.entries):
            raise ValueError(f"duplicate store id: {validated.id}")
        path = self.directory / INGEST_FILENAME
        current = load_entries(path) if path.exists() else []
        current.append(validated)
        _write_entries(path, current)
        self.reload()
        return validated

    def format_hits(self, hits: list[tuple[StoreEntry, float]]) -> str:
        if not hits:
            return "(none retrieved)"
        blocks = []
        for entry, score in hits:
            blocks.append(
                "\n".join(
                    [
                        f"id: {entry.id}",
                        f"domain: {entry.domain}",
                        f"retrieval_score: {score:.3f}",
                        f"selection_process: {entry.selection_process}",
                        f"survivor_pattern: {entry.survivor_pattern}",
                        f"non_survivor_evidence: {entry.non_survivor_evidence}",
                        f"confidence: {entry.confidence}",
                        f"provenance: {entry.provenance}",
                    ]
                )
            )
        return "\n---\n".join(blocks)
