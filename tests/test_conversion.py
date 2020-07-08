# -*- coding: utf-8 -*-
#
# This file is part of caltechdata_api.
#
# Copyright (C) 2020 Caltech.
#
# caltechdata_api is free software; you can redistribute it and/or modify it
# under the terms of the Revised BSD License; see LICENSE file for
# more details.

"""Tests for format transformations."""

import pytest
from datacite.schema43 import validate, validator

from caltechdata_api import decustomize_schema
from helpers import load_json_path

#def validate_json(minimal_json, extra_json):
#    """Validate specific property."""
#    data = {}
#    data.update(minimal_json)
#    data.update(extra_json)
#    validator.validate(data)

CALTECHDATA_FILES = [
    'data/caltechdata/210.json',
    'data/caltechdata/266.json',
    'data/caltechdata/267.json',
    'data/caltechdata/268.json',
    'data/caltechdata/283.json',
    'data/caltechdata/293.json',
    'data/caltechdata/301.json',
    'data/caltechdata/970.json',
    'data/caltechdata/1171.json',
    'data/caltechdata/1235.json',
    'data/caltechdata/1250.json',
    'data/caltechdata/1259.json',
    'data/caltechdata/1300.json',
]


@pytest.mark.parametrize('example_caltechdata', CALTECHDATA_FILES)
def test_example_json_validates(example_caltechdata):
    """Test the example file validates against the JSON schema after
    decustomizing to DataCite."""
    example_json = load_json_path(example_caltechdata)
    datacite = decustomize_schema(example_json,'43')
    validator.validate(datacite)
