"""caltechdata_accept passes its verify argument to every request it makes.

No network is used: requests is replaced by a fake that records the keyword
arguments of each call.
"""

from types import SimpleNamespace
from unittest import mock

import pytest
import requests

from caltechdata_api import caltechdata_accept

ACCEPT = "https://data.caltechlibrary.dev/api/requests/r1/actions/accept"


@pytest.fixture
def calls():
    """Replace requests.get/post; each call is recorded as (method, url, kwargs).

    The draft's review link is missing (404) so the request list is read too,
    which makes the run use every call caltechdata_accept has.
    """
    seen = []

    def get(url, *args, **kwargs):
        seen.append(("GET", url, kwargs))
        if url.endswith("/draft/review"):
            return SimpleNamespace(status_code=404, text="no review")
        hits = {"hits": {"hits": [{"links": {"actions": {"accept": ACCEPT}}}]}}
        return SimpleNamespace(status_code=200, json=lambda: hits)

    def post(url, *args, **kwargs):
        seen.append(("POST", url, kwargs))
        return SimpleNamespace(status_code=200, json=lambda: {}, text="")

    with mock.patch.multiple(requests, get=get, post=post):
        yield seen


@pytest.mark.parametrize("verify", [True, False])
def test_verify_reaches_every_request(calls, verify):
    caltechdata_accept(["abcde-12345"], token="t", verify=verify)
    assert [m for m, _, _ in calls] == ["GET", "GET", "POST"]
    for method, url, kwargs in calls:
        assert kwargs.get("verify", True) is verify, f"{method} {url}"


def test_verify_defaults_to_true(calls):
    caltechdata_accept(["abcde-12345"], token="t")
    for method, url, kwargs in calls:
        assert kwargs.get("verify", True) is True, f"{method} {url}"
