<!--
Copyright 2026 Guzino (https://github.com/guzino)
SPDX-License-Identifier: Apache-2.0
-->

# Incoming critic logs

Live (or fixture) critic runs land here as JSONL via `python eval/log_incoming.py`. The `*.jsonl` files are gitignored.

This directory is quarantine. Rows are not gold. Do not copy them into `train.jsonl` or `heldout.jsonl` from this script. Promotion is a human pull request (new query ids preferred; overlay for edits to existing ids).
