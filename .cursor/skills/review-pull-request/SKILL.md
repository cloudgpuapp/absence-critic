---
name: review-pull-request
description: Review an AbsenceCritic GitHub pull request for Wald isolation, SOLID, and fixture tests. Use when reviewing a PR, pull request, code review, or reviewing branch changes before merge.
---

# Review a pull request

Read [AGENTS.md](../../../AGENTS.md). Then inspect the PR diff, not only the latest commit.

## Gather

```bash
gh pr view <n> --json title,body,author,baseRefName,headRefName,files,commits
gh pr diff <n>
```

If reviewing local uncommitted work, use `git diff` / `git diff main...HEAD` instead.

## Block (must fix)

1. Generator receives store hits, or draft+critic collapsed into one prompt.
2. Import direction: `domain/` → application/adapters; `application/` → adapters.
3. SOLID: loop edited for a new vendor; mega-port; CLI owning loop policy; HTTP in domain.
4. LangChain / LangGraph / DSPy (Phase 0–1).
5. Store entry without `provenance`; invented failure anecdotes.
6. Secrets, `.env`, or SPDX missing on new source files.
7. Origin `docs/` rewritten without an explicit ask.
8. Tests/eval not run or CI fixture job skipped in spirit (no live keys in CI).

## Check but do not block on taste

Prompt wording, comment style, extra fixtures that still pass architecture.

## Report

Use this shape:

```
Verdict: approve | request changes
Blockers: …
SOLID: pass | fail (principle + file)
Wald invariant: pass | fail
Tests: pytest / fixture eval (ran or inferred from CI)
Nits: …
```

Post GitHub review comments only if the user asked to submit the review (`gh pr review`). Otherwise print the report in chat.

Do not merge, do not push to `main`, do not “fix” origin docs while repairing the PR unless that was the task.
