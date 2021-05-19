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

from caltechdata_api import download_url, download_file

def test_download():
    """Test that downloads from the DataCite Media API work."""
    example_doi = '10.22002/D1.1945'
    expected_url = 'https://data.caltech.edu/tindfiles/serve/0cedc067-1ff0-4fc9-871a-2869f3a4957d/'
    assert expected_url == download_url(example_doi)
