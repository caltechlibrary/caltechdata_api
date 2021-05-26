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
from datacite.schema40 import validator as validator4
from datacite.schema43 import validator as validator43

from caltechdata_api import decustomize_schema
from helpers import load_json_path, write_json_path

CALTECHDATA_FILES = [
    "data/caltechdata/210.json",
    "data/caltechdata/266.json",
    "data/caltechdata/267.json",
    "data/caltechdata/268.json",
    "data/caltechdata/283.json",
    "data/caltechdata/293.json",
    "data/caltechdata/301.json",
    "data/caltechdata/970.json",
    "data/caltechdata/1171.json",
    "data/caltechdata/1235.json",
    "data/caltechdata/1250.json",
    "data/caltechdata/1259.json",
    "data/caltechdata/1300.json",
]

DATACITE4_FILES = [
    "data/datacite4/210.json",
    "data/datacite4/266.json",
    "data/datacite4/267.json",
    "data/datacite4/268.json",
    "data/datacite4/283.json",
    "data/datacite4/293.json",
    "data/datacite4/301.json",
    "data/datacite4/970.json",
    "data/datacite4/1171.json",
    "data/datacite4/1235.json",
    "data/datacite4/1250.json",
    "data/datacite4/1259.json",
    "data/datacite4/1300.json",
]


@pytest.mark.parametrize("example_caltechdata", CALTECHDATA_FILES)
def test_example_json_validates(example_caltechdata):
    """Test the example file validates against the JSON schema after
    decustomizing to DataCite."""
    example_json = load_json_path(example_caltechdata)
    datacite4 = decustomize_schema(example_json)
    validator4.validate(datacite4)
    example_json = load_json_path(example_caltechdata)
    datacite43 = decustomize_schema(example_json, schema="43")
    validator43.validate(datacite43)
    outname = example_caltechdata.split("/")[-1]
    write_json_path(f"data/datacite43/{outname}", datacite43)
