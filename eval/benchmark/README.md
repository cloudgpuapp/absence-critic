<!--
Copyright 2026 Guzino (https://github.com/guzino)
SPDX-License-Identifier: Apache-2.0
-->

# Survivorship benchmark (skeleton)

Held-out questions with frozen labels. This is not fixture eval 15/15 and not critic JSON.

Labels (human/frozen):

- `should_caveate`
- `should_not_abstain`
- `must_mention_missing_data`

Score an answer file without running AbsenceCritic:

```bash
python eval/benchmark/score.py --answers path/to/answers.jsonl
```

Each answer row: `{"id": "water-formula", "answer": "H2O"}`. Optional `abstained` bool.

Do not treat `score()` critique `survivorship_risk` as the gold label for this set. Do not train on these ids.
