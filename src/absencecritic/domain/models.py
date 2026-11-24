# Copyright 2026 Guzino (https://github.com/guzino)
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ConfidenceAdjustment(str, Enum):
    lower = "lower"
    abstain = "abstain"
    seek_more_data = "seek_more_data"
    unchanged = "unchanged"


class NonSurvivorHit(BaseModel):
    id: str
    summary: str
    provenance: str
    confidence: float = Field(ge=0.0, le=1.0)


class Critique(BaseModel):
    selection_filter: str
    visible_damage: list[str] = Field(default_factory=list)
    empty_regions: list[str] = Field(default_factory=list)
    non_survivors: list[NonSurvivorHit] = Field(default_factory=list)
    unknown_lethality: list[str] = Field(default_factory=list)
    survivorship_risk: float = Field(ge=0.0, le=1.0)
    confidence_adjustment: ConfidenceAdjustment
    caveats: list[str] = Field(default_factory=list)
    missing_categories: list[str] = Field(default_factory=list)
    suggested_queries: list[str] = Field(default_factory=list)


class StoreEntry(BaseModel):
    id: str
    domain: str
    selection_process: str
    survivor_pattern: str
    non_survivor_evidence: str
    confidence: float = Field(ge=0.0, le=1.0)
    provenance: str
    source_path: Optional[str] = None


@dataclass
class PipelineResult:
    query: str
    draft: str
    retrieved_ids: list[str] = field(default_factory=list)
    critique: Optional[Critique] = None
    final: str = ""
    shielded: bool = True
