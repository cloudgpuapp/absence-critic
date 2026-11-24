<!--
Copyright 2026 Guzino (https://github.com/guzino)
SPDX-License-Identifier: Apache-2.0
-->

## Summary

<!-- Why this change exists. Not a file list. -->

## Wald invariant

- [ ] Generator still never reads the Non-Survivor Store
- [ ] Critic still emits validated `Critique` JSON (if this PR touches the loop or critic)

## SOLID / layers

- [ ] Change landed in the matching layer (`domain` / `application` / `adapters` / `prompts` / `eval`)
- [ ] New LLM or store is an adapter implementing a port (loop unchanged unless the port changed)
- [ ] Ports stay segregated (`generate` has no store hits)

## Test plan

- [ ] `python -m pytest`
- [ ] `python eval/run_eval.py --provider fixture`
- [ ] Live eval only if this PR claims a live-provider change (no keys in CI)

## Notes

<!-- Origin `docs/` edits need an explicit ask. Do not include secrets. -->
