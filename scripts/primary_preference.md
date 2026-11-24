<!--
Copyright 2026 Guzino (https://github.com/guzino)
SPDX-License-Identifier: Apache-2.0
-->

# Primary-model preference recipe (outside CI)

This is not a Wald loop stage and not a GitHub Actions job. The default generator stays the prompted `--provider`. A DPO checkpoint is an experiment, not a product switch.

## What this trains

The **primary** model, using Track B pairs:

- `prompt`: user query
- `rejected`: unshielded draft
- `chosen`: shielded revision

Critique JSON is metadata, not the chosen string. Do not SFT the generator on critic JSON (that is [`critic_train.md`](critic_train.md)).

Export pairs first:

```bash
python eval/export_pairs.py --provider fixture --out eval/pairs/out.jsonl
python scripts/train_primary.py --pairs eval/pairs/out.jsonl --dry-run
```

Chosen is not a truth label. Feedback/private store ids must stay out of public pair files.

## Fine-tune (your machine)

Run DPO or an equivalent contrastive trainer you already have. This repository does not install CUDA libraries. Attribute the base checkpoint's license.

After training, serve OpenAI-compatible `/v1/chat/completions` and call it as `--provider openai` with `OPENAI_BASE_URL` pointed at that server. Do not add a new default provider in this repo until controls still refuse to abstain.

## What is not a result

If control questions (`eval/benchmark/` water-formula, triangle-degrees, or fixture 2+2) start abstaining or hedging, the run failed (style-caveat collapse). Score answers with `python eval/benchmark/score.py --answers ...`, not with critic `survivorship_risk` as gold.

Loss going down is not Phase 3 done.
