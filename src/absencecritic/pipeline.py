# Copyright 2026 Guzino (https://github.com/guzino)
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from absencecritic.jsonutil import parse_json_object
from absencecritic.paths import default_store_dir
from absencecritic.prompts import (
    CRITIC_SYSTEM,
    DRAFT_SYSTEM,
    REVISE_SYSTEM,
    critic_user_message,
    revise_user_message,
)
from absencecritic.providers.base import LLMProvider
from absencecritic.schemas import Critique
from absencecritic.store import NonSurvivorStore


@dataclass
class PipelineResult:
    query: str
    draft: str
    retrieved_ids: list[str] = field(default_factory=list)
    critique: Optional[Critique] = None
    final: str = ""
    shielded: bool = True


def run(
    query: str,
    *,
    provider: LLMProvider,
    store: Optional[NonSurvivorStore] = None,
    store_dir: Optional[Path] = None,
    shield: bool = True,
    retrieve_k: int = 5,
) -> PipelineResult:
    draft = provider.complete(system=DRAFT_SYSTEM, user=query, stage="draft", query=query)
    if not shield:
        return PipelineResult(
            query=query, draft=draft, final=draft, shielded=False
        )

    if store is None:
        store = NonSurvivorStore(store_dir or default_store_dir())
    hits = store.retrieve(query, draft, k=retrieve_k)
    retrieved_ids = [entry.id for entry, _ in hits]
    store_text = store.format_hits(hits)
    raw_critique = provider.complete(
        system=CRITIC_SYSTEM,
        user=critic_user_message(query, draft, store_text),
        stage="critique",
        query=query,
    )
    critique = Critique.model_validate(parse_json_object(raw_critique))
    revision = provider.complete(
        system=REVISE_SYSTEM,
        user=revise_user_message(query, draft, json.dumps(critique.model_dump(mode="json"))),
        stage="revise",
        query=query,
    )
    return PipelineResult(
        query=query,
        draft=draft,
        retrieved_ids=retrieved_ids,
        critique=critique,
        final=revision,
        shielded=True,
    )
