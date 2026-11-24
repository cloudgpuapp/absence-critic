# Copyright 2026 Guzino (https://github.com/guzino)
# SPDX-License-Identifier: Apache-2.0

"""Queue user failure notes as pending. They do not retrieve until accepted."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from absencecritic.adapters.store.yaml_store import (
    FEEDBACK_DIRNAME,
    PENDING_FILENAME,
    YamlStore,
    _write_entries,
    load_entries,
)
from absencecritic.domain.models import StoreCollection, StoreEntry, StoreStatus

MAX_FEEDBACK_CONFIDENCE = 0.4
UNVERIFIED = "not independently verified"
_PENDING_HEADER = """\
# Copyright 2026 Guzino (https://github.com/guzino)
# SPDX-License-Identifier: Apache-2.0
#
# schema_version: 1
# Pending user feedback. Retrieve ignores these until status is accepted.
"""


def _pending_path(store_dir: Path) -> Path:
    return Path(store_dir) / FEEDBACK_DIRNAME / PENDING_FILENAME


def _stamp_provenance(text: str) -> str:
    body = text.strip()
    if not body:
        raise ValueError("provenance is required")
    if UNVERIFIED not in body.lower():
        body = f"{body}; {UNVERIFIED}"
    return body


def _prepare(entry: StoreEntry) -> StoreEntry:
    stamped = (
        datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    )
    return entry.model_copy(
        update={
            "collection": StoreCollection.feedback,
            "status": StoreStatus.pending,
            "confidence": min(entry.confidence, MAX_FEEDBACK_CONFIDENCE),
            "provenance": _stamp_provenance(entry.provenance),
            "ingested_at": entry.ingested_at or stamped,
        }
    )


def queue_feedback(store_dir: Path, source: Path) -> list[str]:
    store = YamlStore(store_dir)
    path = _pending_path(store_dir)
    current = load_entries(path) if path.exists() else []
    ids: list[str] = []
    known = {e.id for e in store.entries} | {e.id for e in current}
    for raw in load_entries(source):
        prepared = _prepare(raw)
        if prepared.id in known:
            raise ValueError(f"duplicate store id: {prepared.id}")
        current.append(prepared)
        known.add(prepared.id)
        ids.append(prepared.id)
    path.parent.mkdir(parents=True, exist_ok=True)
    _write_entries(path, current, header=_PENDING_HEADER)
    return ids


def accept_feedback(store_dir: Path, entry_id: str) -> None:
    path = _pending_path(store_dir)
    if not path.exists():
        raise ValueError(f"no pending feedback at {path}")
    rows = load_entries(path)
    found = False
    updated: list[StoreEntry] = []
    for row in rows:
        if row.id == entry_id:
            found = True
            updated.append(
                row.model_copy(update={"status": StoreStatus.accepted})
            )
        else:
            updated.append(row)
    if not found:
        raise ValueError(f"pending id not found: {entry_id}")
    _write_entries(path, updated, header=_PENDING_HEADER)
