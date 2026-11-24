# Copyright 2026 Guzino (https://github.com/guzino)
# SPDX-License-Identifier: Apache-2.0

import pytest

from absencecritic.jsonutil import parse_json_object


def test_parse_plain_object():
    assert parse_json_object('{"a": 1}') == {"a": 1}


def test_parse_fenced_and_preamble():
    text = 'Here is JSON:\n```json\n{"a": true}\n```\n'
    assert parse_json_object(text) == {"a": True}


def test_parse_rejects_non_object():
    with pytest.raises(ValueError):
        parse_json_object("[1, 2]")
