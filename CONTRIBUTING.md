<!--
Copyright 2026 Guzino (https://github.com/guzino)
SPDX-License-Identifier: Apache-2.0
-->

# Contributing

AbsenceCritic is Apache-2.0. Origin and architecture: [Guzino](https://github.com/guzino).

## Humans

1. Read [`docs/00-README.md`](docs/00-README.md) for the design, then [`AGENTS.md`](AGENTS.md) for the code layout.
2. Keep the Wald invariant: the generator never reads the Non-Survivor Store.
3. Run `python -m pytest` and `python eval/run_eval.py --provider fixture` before a PR. GitHub Actions runs the same pair (fixture provider only; no API keys) on `main` and every pull request.
4. SPDX header on new source files: `Copyright 2026 Guzino (https://github.com/guzino)` / `Apache-2.0`.

## Coding agents

Any tool: treat [`AGENTS.md`](AGENTS.md) as canonical. Do not fork rules per product.

- **Claude Code** loads [`CLAUDE.md`](CLAUDE.md), which points at AGENTS.md and the shared skills.
- **Cursor** loads `.cursor/rules/` and `.cursor/skills/` (skill *bodies* are generic; that directory is only the auto-load location).
- **GitHub Copilot** loads [`.github/copilot-instructions.md`](.github/copilot-instructions.md).

Skills live in one place (`.cursor/skills/*/SKILL.md`) so they cannot drift. Claude should `@` those paths rather than a duplicate `.claude/skills` tree.
