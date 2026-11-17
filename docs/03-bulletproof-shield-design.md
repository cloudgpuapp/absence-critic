<!--
Copyright 2026 Guzinowich
SPDX-License-Identifier: Apache-2.0
-->

# Bulletproof Shield Design

**Document 03 — Technical Architecture of the Wald Module**  
*A second-brain component that reasons about missing data*

---

## 1. Design Goals

The shield is not a replacement for the primary language model. It is a specialized reasoning process that sits beside it and forces consideration of the non-survivors. Its responsibilities are:

1. Detect when a query or draft answer is likely to be affected by survivorship bias.
2. Retrieve or estimate information about the missing cases.
3. Produce a structured critique that the primary model (or a human) can use to revise confidence, add caveats, or change recommendations.
4. Maintain and update a persistent memory of known failure patterns and selection processes.

The primary model remains responsible for fluent generation and broad knowledge. The shield is responsible for the counterfactual: “What would the picture look like if we could see the planes that did not return?”

## 2. High-Level Architecture

```
User Query
    │
    ▼
┌─────────────────────┐
│   Primary LLM       │◄──── Ordinary retrieval / tools
│   (generation)      │
└──────────┬──────────┘
           │ draft + evidence
           ▼
┌─────────────────────┐     ┌──────────────────────┐
│   Wald Module       │◄───►│  Non-Survivor Store  │
│   (shield / critic) │     │  (failure memory)    │
└──────────┬──────────┘     └──────────────────────┘
           │ structured critique
           ▼
┌─────────────────────┐
│   Revision step     │
│   (primary LLM or   │
│    human)           │
└──────────┬──────────┘
           │
           ▼
     Final Answer
     + optional risk annotation
```

The Wald Module can be implemented as:

- A second LLM call with a fixed, carefully engineered system prompt (minimal viable version).
- A smaller fine-tuned critic model.
- A hybrid of rules, retrieval, and a small model.

## 3. The Wald Checklist (Core Reasoning Procedure)

Every invocation of the shield runs a fixed sequence:

1. **Identify the selection filter**  
   What process determined which evidence is visible? (Publication, platform survival, user persistence, benchmark construction, etc.)

2. **Map the visible damage**  
   What patterns, successes, or positive examples are present in the draft and its supporting evidence?

3. **Locate the empty regions**  
   Where is coverage suspiciously thin? Which outcomes, strategies, or populations are underrepresented relative to a plausible prior?

4. **Estimate or retrieve non-survivors**  
   Query the Non-Survivor Store. If nothing is found, apply simple base-rate priors or explicitly mark the region as “unknown lethality.”

5. **Produce the armor recommendation**  
   - Confidence adjustment (lower / abstain / seek more data).  
   - Specific caveats to add.  
   - Concrete missing categories that should be acknowledged or investigated.  
   - Suggested retrieval queries for failure cases.

Output is always structured (JSON or equivalent) so it can be consumed programmatically.

## 4. Non-Survivor Store

A dedicated knowledge base, separate from ordinary retrieval indexes, containing:

- Curated post-mortems, null-result summaries, and abandoned-project descriptions.
- Domain-specific base rates (e.g., startup failure rates by sector, replication rates in a field, known long-tail error modes).
- Explicit models of common selection processes (“papers are more likely to be published if the result is positive and surprising”).
- User- or organization-contributed failure logs (with appropriate access controls).

The store is updated continuously. Agents or humans can add new entries. The Wald Module is the primary reader; the primary LLM does not retrieve from it by default, preventing survivor bias from leaking back in.

## 5. Integration Modes

| Mode | Description | When to Use |
|------|-------------|-------------|
| Always-on critic | Shield runs on every substantial answer | High-stakes or research use |
| On-demand (“Wald mode”) | User or system toggles the shield | Interactive exploration |
| Evaluation harness | Shield scores existing model outputs for survivorship risk | Benchmarking and red-teaming |
| Training signal | Critiques are used as preference or contrastive data | Fine-tuning future models |

## 6. Confidence and Abstention

The shield can emit a scalar “survivorship risk” score. High scores trigger:

- Automatic insertion of caveats.
- A requirement for the primary model to retrieve from the Non-Survivor Store before finalizing.
- Outright abstention when the empty regions are critical and no compensating evidence exists.

This is the operational equivalent of refusing to armor only the visible holes.

## 7. What the Shield Does Not Do

- It does not invent detailed fictional failure cases and present them as fact.
- It does not override the primary model’s factual knowledge when that knowledge is well-supported.
- It does not attempt to reconstruct the exact bullet-hole maps of individual lost planes; it estimates vulnerability at the level of regions and processes.

Its power comes from consistently asking the question the primary model is not trained to ask: where are the holes that are not there?
