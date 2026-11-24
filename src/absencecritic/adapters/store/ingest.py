# Copyright 2026 Guzino (https://github.com/guzino)
# SPDX-License-Identifier: Apache-2.0

"""Curated Non-Survivor Store ingest. CLI stays a thin caller."""

from __future__ import annotations

from pathlib import Path

from absencecritic.adapters.store.yaml_store import (
    INGEST_FILENAME,
    YamlStore,
    load_entries,
)


def ingest_yaml(store_dir: Path, source: Path) -> list[str]:
    source = source.resolve()
    store = YamlStore(store_dir)
    ingest_path = (store.directory / INGEST_FILENAME).resolve()
    if source == ingest_path:
        raise ValueError("cannot ingest the store's ingested.yaml into itself")
    ids: list[str] = []
    for entry in load_entries(source):
        store.add(entry)
        ids.append(entry.id)
    return ids
