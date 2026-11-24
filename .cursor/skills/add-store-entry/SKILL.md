---
name: add-store-entry
description: Add a Non-Survivor Store YAML entry with required provenance and a retrieval smoke check. Use when adding store notes, failure memory, post-mortems, or data/non_survivors entries.
---

# Add store entry

1. Prefer `absencecritic ingest path/to/entries.yaml` (writes `ingested.yaml` in the store directory). Or append by hand to [data/non_survivors/entries.yaml](../../../data/non_survivors/entries.yaml) (or a new YAML file in that directory).
2. Required fields: `id`, `domain`, `selection_process`, `survivor_pattern`, `non_survivor_evidence`, `confidence`, `provenance`.
3. `provenance` is a real citation or `author prior, low confidence`.
4. Quote scalars that contain `:` or inner `"`.
5. Do not invent a specific unpublished event as fact.
6. Smoke: load `YamlStore` and `retrieve` a query that should rank this `id` in the top hits.
7. SPDX on new files. Do not change `WaldLoop` for a data add.
