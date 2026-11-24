# Copyright 2026 Guzino (https://github.com/guzino)
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path

_DIR = Path(__file__).parent
DRAFT_SYSTEM = (_DIR / "draft.md").read_text(encoding="utf-8").strip()
CRITIC_SYSTEM = (_DIR / "critic.md").read_text(encoding="utf-8").strip()
REVISE_SYSTEM = (_DIR / "revise.md").read_text(encoding="utf-8").strip()


def critic_user_message(query: str, draft: str, store_hits: str) -> str:
    return (
        f"User query:\n{query}\n\n"
        f"Draft answer (from the primary model; it did not see the Non-Survivor Store):\n{draft}\n\n"
        f"Retrieved Non-Survivor Store entries (may be empty):\n{store_hits}\n"
    )


def revise_user_message(query: str, draft: str, critique_json: str) -> str:
    return (
        f"User query:\n{query}\n\n"
        f"Draft answer:\n{draft}\n\n"
        f"AbsenceCritic JSON critique:\n{critique_json}\n"
    )
