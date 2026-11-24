<!--
Copyright 2026 Guzino (https://github.com/guzino)
SPDX-License-Identifier: Apache-2.0
-->

# Phase 2 working plan: Specialized Critic

Not an origin document. Spec remains Document 04 Phase 2. Origin `docs/` stay frozen.

Phase 1 left a prompted critic plus fixtures. Phase 2 is a **dataset and then a model**, not a new graph.

## Wald pass

**Visible:** 15 recorded (query, draft, critique, revision) triples; `Critique` JSON is already the training target shape.

**Empty:** No frozen critic-only JSONL; no human-refine loop; no small critic adapter; live Grok critiques are not gold.

**Unknown:** Whether a LoRA on those 15 rows beats the prompt. Do not replace the prompted critic until eval says so.

**Armor:** Do not invent gold critiques. Do not put store hits in `generate`. Do not collapse draft+critic. No LangGraph. Fine-tune stays out of CI (no GPU, no keys).

## Slices

1. **Gold freeze (this PR):** `eval/gold/critiques.jsonl` from fixtures; each critique validates as `Critique`; regenerate with `python eval/export_gold.py`.
2. **Human refine:** optional overlay file for corrected critiques; never silent-overwrite fixtures.
3. **Local critic adapter:** `GeneratorPort`/`CriticPort` pointing at a fine-tuned endpoint; WaldLoop unchanged.
4. **Swap decision:** fixture eval 15/15 and a live spot-check before making the small model the default critic.

Order is 1 then 2 then 3 then 4. Do not skip to fine-tune without a frozen gold file.
