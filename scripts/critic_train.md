<!--
Copyright 2026 Guzino (https://github.com/guzino)
SPDX-License-Identifier: Apache-2.0
-->

# Critic train recipe (outside CI)

This is not a Wald loop stage and not a GitHub Actions job. The prompted critic stays the default until a later swap PR with held-out numbers.

## What this trains

Only the **critic**. The assistant target is `Critique` JSON. Do not SFT the generator on these rows. That would collapse the shield into a hedging style.

Input: [`eval/gold/train.jsonl`](../eval/gold/train.jsonl) after `python eval/export_gold.py` (overlay applied on train/held-out export only).

Do **not** train on `heldout.jsonl` or `critiques.jsonl`.

## Validate and export chat rows

```bash
python scripts/train_critic.py --dry-run
python scripts/train_critic.py --export-chat scripts/out/critic_sft.jsonl
```

Each exported row is system (`prompts/critic.md`) plus user (query, draft, empty store hits) plus assistant (critique JSON). Gold freeze does not record store hit text. Do not invent store entries to fill that hole.

## Base model

Pick a small instruct checkpoint whose license you can comply with. One Apache-2.0 example is Qwen2.5-0.5B-Instruct (`Qwen/Qwen2.5-0.5B-Instruct`). Attribute the base model in any derived adapter you publish. AbsenceCritic does not vendor those weights.

## Fine-tune (your machine)

Use PEFT/LoRA or an equivalent tool you already run. This repository does not install CUDA libraries. After training, serve an OpenAI-compatible `/v1/chat/completions` endpoint (vLLM, llama.cpp, a local proxy).

Then point AbsenceCritic at it without changing the loop:

```bash
# PowerShell
$env:ABSENCECRITIC_LOCAL_BASE_URL = "http://127.0.0.1:8080/v1"
$env:ABSENCECRITIC_LOCAL_CRITIC_MODEL = "your-adapter-name"
$env:ABSENCECRITIC_LOCAL_API_KEY = "local"
absencecritic --provider fixture --critic local "What works for launching a startup?"
```

## What is not a result

Training loss going down is not Phase 2 done. Fixture 15/15 after training on those same 15 rows is leakage. Report held-out gold, then a swap PR (slice G) if the bars in `plans/phase-2.md` pass.
