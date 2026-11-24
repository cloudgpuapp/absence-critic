---
name: run-phase-eval
description: Run AbsenceCritic Phase 0 pytest and fixture eval. Use when verifying the Wald loop, after pipeline or fixture changes, or when the user asks to run eval.
---

# Run phase eval

Default is fixtures (no API key).

```bash
python -m pytest
python eval/run_eval.py --provider fixture
```

Live provider only if the user asked:

```bash
python eval/run_eval.py --provider openai
```

Report pytest counts and eval `passed/total`. If a biased case fails missing-data language, fix the **fixture revision** or scorer - do not weaken domain invariants. If a control abstains, that is a fail.

GitHub Actions (`.github/workflows/ci.yml`) runs the fixture pair only. Do not add `OPENAI_API_KEY` to CI.
