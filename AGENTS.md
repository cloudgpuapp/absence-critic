<!--
Copyright 2026 Guzino (https://github.com/guzino)
SPDX-License-Identifier: Apache-2.0
-->

# AbsenceCritic agent guide

Ports-and-adapters around a linear Wald loop. Not LangGraph. Not a single mega-prompt.

**Invariant:** the generator never reads the Non-Survivor Store. Only the critic does.

## Layers

| Layer | Path | May import | Must not |
|-------|------|------------|----------|
| Domain | `src/absencecritic/domain/` | stdlib, pydantic | I/O, prompts, HTTP, adapters, application |
| Application | `src/absencecritic/application/` | domain, ports, stdlib | adapters, HTTP, YAML files |
| Prompts | `src/absencecritic/prompts/` | stdlib | pipeline logic, store I/O |
| Adapters | `src/absencecritic/adapters/` | domain, application.ports, prompts, I/O | other adapters' internals, collapsing stages |
| Eval | `eval/` | public facade / adapters | rewriting domain models |
| Origin docs | `docs/` | — | edits unless the user asked |

Public API: `from absencecritic import run, Critique, StoreEntry, PipelineResult`.

## Where a change goes

- New field on a critique or store entry → `domain/`
- Loop steps (draft → retrieve → critique → revise) → `application/`
- Prompt wording → `src/absencecritic/prompts/`
- HTTP, fixtures, YAML store, CLI → `adapters/`
- New LLM backend → `adapters/llm/` implementing `GeneratorPort` and `CriticPort`; do not edit `WaldLoop` unless the port itself changes
- New store backend → `adapters/store/` implementing `StorePort`
- Eval queries/fixtures → `eval/`

## Forbidden

- LangChain, LangGraph, DSPy in Phase 0–1
- Passing store hits into `generate`
- Inventing failure anecdotes not in the store or critique
- Store entries without `provenance`
- Business logic in the CLI
- Rewriting `docs/` origin documents unless asked

## Cursor surface

- Rules: `.cursor/rules/`
- Skills: `.cursor/skills/` (`architecture-guard`, `add-store-entry`, `add-llm-adapter`, `run-phase-eval`)
- Commands: `/check-architecture`, `/new-store-entry`, `/new-provider`, `/run-eval`

SPDX on every new source file:

```
Copyright 2026 Guzino (https://github.com/guzino)
SPDX-License-Identifier: Apache-2.0
```
