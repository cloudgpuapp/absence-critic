---
name: architecture-guard
description: Check AbsenceCritic diffs for ports-and-adapters import direction and Wald stage isolation. Use when adding files, moving modules, reviewing PRs, refactoring, or when the user asks to check architecture.
---

# Architecture guard

Read [AGENTS.md](../../../AGENTS.md) (canonical for every tool). Then inspect the diff (or named files).

## Checks

1. `domain/` imports only stdlib/pydantic — never `application` or `adapters`.
2. `application/` never imports `adapters`.
3. `WaldLoop` does not pass store hits into `generate`.
4. Critic path parses/validates `Critique`; generator path does not load the store.
5. No new LangChain/LangGraph/DSPy dependency.
6. New code sits in the matching layer (see AGENTS.md table).
7. SPDX header present on new source files.
8. SOLID mapping in AGENTS.md: no collapsed stages, no loop edit for a new vendor, ports stay segregated.

## Report

List violations first, then a one-line verdict: pass or fail. If fail, say the exact file and the rule broken. Do not "fix" origin `docs/` while repairing architecture.
