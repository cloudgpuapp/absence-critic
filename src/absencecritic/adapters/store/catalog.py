# Copyright 2026 Guzino (https://github.com/guzino)
# SPDX-License-Identifier: Apache-2.0

"""Map a frozen citable catalog into StoreEntry rows. No HTTP."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from absencecritic.adapters.store.yaml_store import YamlStore
from absencecritic.domain.models import StoreCollection, StoreEntry

_REQUIRED = (
    "id",
    "domain",
    "selection_process",
    "survivor_pattern",
    "non_survivor_evidence",
    "confidence",
    "provenance",
    "source_url",
)


def _rows(raw: object) -> list[object]:
    if raw is None:
        return []
    if isinstance(raw, list):
        return raw
    if isinstance(raw, dict):
        for key in ("catalog", "sources", "entries"):
            if key in raw:
                value = raw[key]
                if not isinstance(value, list):
                    raise ValueError(f"catalog key {key!r} must be a list")
                return value
        return [raw]
    raise ValueError("catalog must be a list or a mapping with catalog/sources/entries")


def _load_raw(path: Path) -> object:
    text = path.read_text(encoding="utf-8")
    suffix = path.suffix.lower()
    if suffix in {".yaml", ".yml"}:
        return yaml.safe_load(text)
    if suffix == ".jsonl":
        return [json.loads(line) for line in text.splitlines() if line.strip()]
    if suffix == ".json":
        return json.loads(text)
    raise ValueError(f"unsupported catalog suffix: {path.suffix}")


def catalog_to_entry(item: object) -> StoreEntry:
    if not isinstance(item, dict):
        raise ValueError("each catalog row must be a mapping")
    missing = [key for key in _REQUIRED if not str(item.get(key, "")).strip()]
    if missing:
        raise ValueError(f"catalog row missing {', '.join(missing)}")
    url = str(item["source_url"]).strip()
    if not url.startswith(("http://", "https://")):
        raise ValueError(f"source_url must be http(s): {url!r}")
    collection = item.get("collection") or StoreCollection.catalog
    entry = StoreEntry.model_validate(
        {
            "id": item["id"],
            "domain": item["domain"],
            "selection_process": item["selection_process"],
            "survivor_pattern": item["survivor_pattern"],
            "non_survivor_evidence": item["non_survivor_evidence"],
            "confidence": item["confidence"],
            "provenance": item["provenance"],
            "collection": collection,
            "source_url": url,
        }
    )
    if entry.collection is not StoreCollection.catalog:
        raise ValueError("catalog ingest requires collection=catalog")
    return entry


def load_catalog(path: Path) -> list[StoreEntry]:
    return [catalog_to_entry(row) for row in _rows(_load_raw(path))]


def ingest_catalog(store_dir: Path, source: Path) -> list[str]:
    store = YamlStore(store_dir)
    ids: list[str] = []
    for entry in load_catalog(source):
        store.add(entry)
        ids.append(entry.id)
    return ids
