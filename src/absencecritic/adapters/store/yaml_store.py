# Copyright 2026 Guzino (https://github.com/guzino)
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

import yaml

from absencecritic.domain.models import (
    MAX_AUTHOR_PRIOR_CONFIDENCE,
    StoreCollection,
    StoreEntry,
    StoreEvidence,
    StoreStatus,
)

INGEST_FILENAME = "ingested.yaml"
FEEDBACK_DIRNAME = "feedback"
PENDING_FILENAME = "pending.yaml"
_INGEST_HEADER = """\
# Copyright 2026 Guzino (https://github.com/guzino)
# SPDX-License-Identifier: Apache-2.0
#
# schema_version: 1
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
    "when",
    "where",
    "which",
    "who",
    "whom",
    "whose",
    "with",
}


def _write_entries(
    path: Path, entries: list[StoreEntry], header: str = _INGEST_HEADER
) -> None:
    payload = [
        e.model_dump(mode="json", exclude={"source_path"}, exclude_none=True)
        for e in entries
    ]
    body = yaml.safe_dump(payload, sort_keys=False, allow_unicode=True)
    path.write_text(header + "\n" + body, encoding="utf-8")


_METHOD_TOKENS = frozenset(
    {
        "abraham",
        "armor",
        "bias",
        "critic",
        "insight",
        "module",
        "quote",
        "shield",
        "survivor",
        "survivors",
        "survivorship",
        "wald",
    }
)
_ADVICE_CUES = frozenset(
    {
        "advice",
        "always",
        "best",
        "founder",
        "founders",
        "guaranteed",
        "launch",
        "launched",
        "launching",
        "should",
        "success",
        "successful",
        "tips",
        "treatment",
        "tricks",
        "work",
        "works",
    }
)
_MIN_OVERLAP = 2
_SCORE_RATIO = 0.5


def tokenize(text: str) -> set[str]:
    return {t for t in _TOKEN.findall(text.lower()) if t not in _STOP and len(t) > 1}


def _related(left: str, right: str) -> bool:
    if left == right:
        return True
    if min(len(left), len(right)) < 5:
        return False
    return left.startswith(right) or right.startswith(left)


def _domain_hit(domain: str, content: set[str]) -> bool:
    domain_tokens = tokenize(domain.replace("_", " "))
    return any(
        _related(dt, ct) for dt in domain_tokens for ct in content
    )


def _query_content(query: str, draft: str) -> set[str]:
    q = tokenize(query)
    meta = bool(q & {"wald", "abraham", "quote"}) and not (q & _ADVICE_CUES)
    if meta:
        return q - _METHOD_TOKENS
    combined = tokenize(f"{query} {draft}")
    content = combined - _METHOD_TOKENS
    if content:
        return content
    if tokenize(draft) & _ADVICE_CUES:
        return combined
    return set()


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
        if "entries" in raw:
            raw = raw["entries"]
        else:
            raw = [raw]
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

    def _iter_files(self) -> list[Path]:
        files: list[Path] = []
        for path in self.directory.iterdir():
            # Nested private/ is gitignored and not retrieved. Org memory is a
            # separate ABSENCECRITIC_STORE directory, not this folder.
            if path.name == "private" and path.is_dir():
                continue
            if path.suffix.lower() in {".yaml", ".yml", ".json", ".jsonl"}:
                files.append(path)
        extra = self.directory / FEEDBACK_DIRNAME
        if extra.is_dir():
            for path in extra.iterdir():
                if path.suffix.lower() in {".yaml", ".yml", ".json", ".jsonl"}:
                    files.append(path)
        return sorted(files)

    def reload(self) -> None:
        self.entries = []
        if not self.directory.exists():
            raise FileNotFoundError(f"Non-Survivor Store not found: {self.directory}")
        for path in self._iter_files():
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
        content = _query_content(query, draft)
        if not content:
            return []
        scored: list[tuple[int, float]] = []
        for i, bag in enumerate(self._bags):
            entry = self.entries[i]
            if entry.status is StoreStatus.pending:
                continue
            if (
                entry.collection is StoreCollection.feedback
                and entry.status is not StoreStatus.accepted
            ):
                continue
            overlap = content & bag
            id_tokens = {
                tok for tok in tokenize(entry.id) - _METHOD_TOKENS if len(tok) >= 4
            }
            id_hit = bool(id_tokens & content)
            domain_hit = _domain_hit(entry.domain, content)
            if not overlap and not domain_hit and not id_hit:
                continue
            if len(overlap) < _MIN_OVERLAP and not domain_hit and not id_hit:
                continue
            score = len(overlap) / len(content)
            if domain_hit:
                score += 0.15
            if id_hit:
                score += 0.05
            scored.append((i, score))
        scored.sort(key=lambda item: item[1], reverse=True)
        if not scored:
            return []
        floor = scored[0][1] * _SCORE_RATIO
        kept = [(i, score) for i, score in scored if score >= floor]
        return [(self.entries[i], score) for i, score in kept[:k]]

    def add(self, entry: StoreEntry) -> StoreEntry:
        """Append a validated entry to ingested.yaml. Retrieve-only StorePort is unchanged."""
        validated = StoreEntry.model_validate(
            entry.model_dump(exclude={"source_path"}, exclude_none=True)
        )
        if not validated.provenance.strip():
            raise ValueError("provenance is required")
        if (
            validated.evidence is StoreEvidence.author_prior
            and validated.confidence > MAX_AUTHOR_PRIOR_CONFIDENCE
        ):
            raise ValueError(
                f"author_prior confidence must be <= {MAX_AUTHOR_PRIOR_CONFIDENCE}"
            )
        if any(existing.id == validated.id for existing in self.entries):
            raise ValueError(f"duplicate store id: {validated.id}")
        if not validated.ingested_at:
            stamped = (
                datetime.now(timezone.utc).replace(microsecond=0).isoformat()
            )
            validated = validated.model_copy(update={"ingested_at": stamped})
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
                        f"evidence: {entry.evidence.value}",
                        f"provenance: {entry.provenance}",
                    ]
                )
            )
        return "\n---\n".join(blocks)
