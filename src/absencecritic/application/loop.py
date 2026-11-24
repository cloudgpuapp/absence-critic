# Copyright 2026 Guzino (https://github.com/guzino)
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from absencecritic.application.jsonutil import parse_json_object
from absencecritic.application.ports import CriticPort, GeneratorPort, StorePort
from absencecritic.domain.models import Critique, PipelineResult


def run(
    query: str,
    *,
    provider: Optional[object] = None,
    generator: Optional[GeneratorPort] = None,
    critic: Optional[CriticPort] = None,
    store: Optional[StorePort] = None,
    store_dir: Optional[Path] = None,
    shield: bool = True,
    retrieve_k: int = 5,
) -> PipelineResult:
    """Wald loop. `provider` may implement both LLM ports; calls stay separate."""
    del store_dir  # adapters construct the store; kept for call-site compatibility
    gen = generator or provider
    cri = critic or provider
    if gen is None:
        raise TypeError("run() requires generator= or provider=")
    draft = gen.generate(query=query)
    if not shield:
        return PipelineResult(query=query, draft=draft, final=draft, shielded=False)
    if store is None:
        raise TypeError("run() requires store= when shield=True")
    if cri is None:
        raise TypeError("run() requires critic= or provider= when shield=True")
    hits = store.retrieve(query, draft, k=retrieve_k)
    retrieved_ids = [entry.id for entry, _ in hits]
    raw_critique = cri.critique(
        query=query, draft=draft, store_hits=store.format_hits(hits)
    )
    critique = Critique.model_validate(parse_json_object(raw_critique))
    revision = gen.revise(
        query=query,
        draft=draft,
        critique_json=json.dumps(critique.model_dump(mode="json")),
    )
    return PipelineResult(
        query=query,
        draft=draft,
        retrieved_ids=retrieved_ids,
        critique=critique,
        final=revision,
        shielded=True,
    )
