---
name: open-pull-request
description: Open a GitHub pull request for AbsenceCritic against main. Use when the user asks to open, create, or file a PR, pull request, or to land work off main.
---

# Open a pull request

Read [AGENTS.md](../../../AGENTS.md) (SOLID + PR sections). Policy is there; this file is the procedure.

## Do not

- Push feature commits to `main`.
- Commit `.env`, keys, or secret-bearing logs.
- Skip pytest / fixture eval.
- Rewrite origin `docs/` unless the user asked.
- Open a PR that mixes unrelated layers (split instead).

## Steps

1. `git status`, `git diff`, `git log` and `git diff main...HEAD` (or the default branch). Confirm `.env` is untracked.
2. Run the architecture-guard skill on the branch diff.
3. Run `python -m pytest` and `python eval/run_eval.py --provider fixture`. Live eval only if the user asked.
4. Check SOLID: new backends are adapters; loop/ports unchanged unless the contract changed; generate still has no store hits.
5. Create/switch a branch if still on `main` (`feat/…`, `fix/…`, `docs/…`).
6. Commit only if the user asked. Push with `git push -u origin HEAD`.
7. `gh pr create` using `.github/pull_request_template.md`. Title states the why. Body: summary, Wald invariant, SOLID/layer, fixture test plan.
8. Return the PR URL. Do not merge unless the user asked.

Windows: use `gh`; do not invent a GitHub API client.
