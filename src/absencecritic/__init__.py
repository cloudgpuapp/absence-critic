# Copyright 2026 Guzino (https://github.com/guzino)
# SPDX-License-Identifier: Apache-2.0

"""AbsenceCritic: a survivorship-bias shield for language models."""

from absencecritic.pipeline import PipelineResult, run
from absencecritic.schemas import Critique, StoreEntry

__all__ = ["Critique", "PipelineResult", "StoreEntry", "run"]
__version__ = "0.1.0"
