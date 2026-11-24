<!--
Copyright 2026 Guzino (https://github.com/guzino)
SPDX-License-Identifier: Apache-2.0
-->

# Survivorship benchmark

Held-out questions with frozen labels. This is not fixture eval 15/15 and not critic JSON.

Labels (human/frozen):

- `should_caveate`
- `should_not_abstain`
- `must_mention_missing_data`

Run baseline and shielded arms, then score. The regex scorer still matches words like "unknown"; the rubric judge (labelled `benchmark-rubric-heuristic` or `benchmark-rubric-llm`) does not call the critic under test. The report includes agreement between them.

```bash
python eval/benchmark/run.py --provider fixture --out eval/benchmark/answers.jsonl
python eval/benchmark/score.py --answers eval/benchmark/answers.jsonl
```

Each answer row: `{"id": "water-formula", "answer": "H2O"}`. Optional `arm` and `abstained` bool. `--judge none` skips the rubric. `--judge openai` is a separate live call, not `critic.critique`.

Do not treat `score()` critique `survivorship_risk` as the gold label for this set. Do not train on these ids.
