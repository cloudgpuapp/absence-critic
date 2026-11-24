# Copyright 2026 Guzino (https://github.com/guzino)
# SPDX-License-Identifier: Apache-2.0

from absencecritic.adapters.llm.fixture import FixtureLLM
from absencecritic.adapters.llm.local import LocalCritic
from absencecritic.adapters.llm.openai_compat import OpenAICompat

__all__ = ["FixtureLLM", "LocalCritic", "OpenAICompat"]
