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


@pytest.mark.skip(reason="works, don't want to do unnecessary downloads")
def test_download():
    """Test that downloads from the DataCite Media API work."""
    example_doi = "10.22002/D1.1098"
    expected_url = (
        "https://data.caltech.edu/tindfiles/serve/293d37c5-73f2-4016-bcd5-76cf353ff9d8/"
    )
    assert expected_url == download_url(example_doi)
    filen = download_file(example_doi)
    assert filen == "10.22002-D1.1098"
