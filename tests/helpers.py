# -*- coding: utf-8 -*-
#
# This file is part of DataCite.
#
# Copyright (C) 2015, 2016 CERN.
#
# DataCite is free software; you can redistribute it and/or modify it
# under the terms of the Revised BSD License; see LICENSE file for
# more details.

"""Test helpers."""

from __future__ import absolute_import, print_function

import io
import json
import os
from os.path import dirname, join


def load_json_path(path):
    """Helper method for loading a JSON example file from a path."""
    path_base = dirname(__file__)
    with io.open(join(path_base, path), encoding='utf-8') as file:
        content = file.read()
    return json.loads(content)

