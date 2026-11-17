<!--
Copyright 2026 Guzino (https://github.com/guzino)
SPDX-License-Identifier: Apache-2.0
-->

# Bulletproof Model Shield — Design Package Index

**Program**: Armor the Places With No Holes  
**Origin**: Abraham Wald’s 1943 aircraft vulnerability analysis, extended to modern language models

This package contains the complete engineering narrative and technical design for attaching a survivorship-bias shield (“Wald Module” / second brain) to large language models.

## Documents

| File | Title | Purpose |
|------|--------|---------|
| `01-wald-origin.md` | From Wald’s Notebook: The Armor That Is Not There | Historical and conceptual foundation, stated from the original insight |
| `02-missing-planes-in-llms.md` | The Missing Planes in the Training Corpus | Precise mapping of the problem onto contemporary LLMs and their data |
| `03-bulletproof-shield-design.md` | Bulletproof Shield Design | Architecture, checklist, Non-Survivor Store, and integration modes |
| `04-implementation-roadmap.md` | Implementation Roadmap and Engineering Notes | Phased construction plan from minimal viable critic to full system |

## How to Read

1. Start with Document 01 to internalize the core inversion: visible damage ≠ critical vulnerability.
2. Read Document 02 to see exactly how that inversion appears in training corpora, retrieval, and evaluation.
3. Use Document 03 as the technical specification for the shield component.
4. Follow Document 04 to build it.

## Core Claim

A model trained only on the planes that returned will correctly learn the distribution of survivable damage. Robustness requires an explicit, persistent process that reasons about the planes that did not return and adjusts recommendations accordingly. That process is the shield.

---

*All documents in this package are intended to be used together. No detail from the design discussions has been omitted.*
