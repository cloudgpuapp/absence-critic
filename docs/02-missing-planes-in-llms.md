<!--
Copyright 2026 Guzino (https://github.com/guzino)
SPDX-License-Identifier: Apache-2.0
-->

# The Missing Planes in the Training Corpus

**Document 02 — The Problem Statement for Large Language Models**  
*Engineering analysis of survivorship bias in contemporary AI systems*

---

## 1. The Returning Bombers Are the Published Text

A modern large language model is trained by next-token prediction on a vast corpus of human-generated text. That corpus is not a random sample of possible thoughts, actions, or outcomes. It is the set of texts that survived multiple filters:

- Someone chose to write it down.
- Someone chose to publish, post, or archive it.
- It was not removed by platform policy, legal action, or simple neglect.
- It was not so uninteresting, unsuccessful, or private that no one bothered to record it.
- In later stages it may have been further filtered by preference data (RLHF) that itself reflects what annotators preferred among the options they were shown.

The model therefore learns the statistical patterns of *survivors*. It becomes extremely good at producing text that looks like the text that already exists. It has far less information about the texts that were never written, the experiments that failed quietly, the strategies that were tried and abandoned, and the base rates of outcomes that do not generate documentation.

## 2. Concrete Forms of the Missing Data

| Domain | What We See (Survivors) | What Is Systematically Missing (Non-survivors) |
|--------|--------------------------|------------------------------------------------|
| Scientific literature | Published positive or interesting results | Null results, abandoned lines of inquiry, failed replications that were never written up |
| Startup / product advice | Post-mortems and success stories from companies that eventually succeeded or that wrote about their failure | The far larger set of attempts that died without a blog post |
| Medical / clinical text | Documented cases that reached publication or electronic health records | Rare diseases, unreported adverse events, outcomes that never entered a record |
| Everyday reasoning | Polished explanations and successful arguments | The private dead-ends, the half-formed ideas that were discarded, the tacit knowledge that was never verbalized |
| Model evaluation | Curated benchmarks and impressive demos | Silent failures in ordinary use, long-tail errors that do not make good papers |

In each case the model can generate fluent, confident continuations in regions where the training data contain almost no counter-examples, because the counter-examples never entered the record.

## 3. Why Ordinary Scaling Does Not Fix It

Additional data drawn from the same selection process simply adds more survivors. The empty regions remain empty. Preference optimization and safety fine-tuning further shape the model toward the subset of outputs that human raters preferred among the candidates they saw; they do not restore the missing failure distribution.

Retrieval-augmented generation, unless deliberately pointed at failure corpora, retrieves more of the same survivor text. Synthesis agents asked for “top themes” or “lessons learned” overweight what was articulated by people who stayed long enough to be interviewed.

## 4. The Observable Symptoms

- High confidence on strategies whose published literature is dominated by successes.
- Under-estimation of base rates of failure.
- Difficulty answering “what has been tried and did not work?”
- Evaluation scores that look strong on benchmarks built from surviving tasks while performance collapses on the unrecorded tail.
- World models (e.g., in driving or planning) that imagine mostly benign futures because the training trajectories almost all ended safely.

These are not primarily failures of reasoning capacity. They are failures of the data-generating process that the model was given. The model is correctly learning the distribution of the planes that came back.

## 5. The Required Correction

Any system that claims to be robust must contain an explicit mechanism for reasoning about the selection filter itself. That mechanism must be able to:

- Recognize when the available evidence is conditional on survival.
- Retrieve or estimate information about the complementary set of non-survivors.
- Adjust the main model’s confidence, recommendations, and generated plans accordingly.
- Surface the places where armor (caution, additional data collection, or abstention) is most needed—the places where the survivors show no damage.

That mechanism is the shield described in the following documents.
