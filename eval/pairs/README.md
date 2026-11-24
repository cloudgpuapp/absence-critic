<!--
Copyright 2026 Guzino (https://github.com/guzino)
SPDX-License-Identifier: Apache-2.0
-->

# Preference pairs

`python eval/export_pairs.py --provider fixture --out eval/pairs/out.jsonl`

JSONL files here are gitignored. `chosen` is the shielded revision, `rejected` is the unshielded draft, `critique` is metadata with store summaries stripped. Feedback/private store ids are refused unless `--allow-private`.
