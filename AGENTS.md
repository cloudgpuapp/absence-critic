<!--
Copyright 2026 Guzino (https://github.com/guzino)
SPDX-License-Identifier: Apache-2.0
-->

# AbsenceCritic agent guide

Tool-agnostic rules for humans and coding agents (Claude Code, Cursor, Copilot, or anything else). Policy lives here. Editor-specific loaders are thin pointers; do not fork these rules per tool.

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

## Workflows

Shared skill files (Agent Skills format; content is generic):

| Workflow | File |
|----------|------|
| Check layer imports and stage isolation | `.cursor/skills/architecture-guard/SKILL.md` |
| Add a Non-Survivor Store entry | `.cursor/skills/add-store-entry/SKILL.md` |
| Add an LLM adapter | `.cursor/skills/add-llm-adapter/SKILL.md` |
| Run pytest and fixture eval | `.cursor/skills/run-phase-eval/SKILL.md` |

The `.cursor/skills/` path is where Cursor auto-loads skills. Claude Code should follow the same files via `CLAUDE.md`. Do not copy the bodies into a second tree.

## Tool adapters (pointers only)

- Claude Code: [`CLAUDE.md`](CLAUDE.md)
- GitHub Copilot: [`.github/copilot-instructions.md`](.github/copilot-instructions.md)
- Cursor: `.cursor/rules/`, `.cursor/skills/`, `.cursor/commands/`
- Humans: [`CONTRIBUTING.md`](CONTRIBUTING.md)

SPDX on every new source file:

```
Copyright 2026 Guzino (https://github.com/guzino)
SPDX-License-Identifier: Apache-2.0
```
