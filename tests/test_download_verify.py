"""download_from_record can target a local instance and skip TLS verification.

A test instance with a self-signed certificate (local=True) needs verify=False
on its requests. A redirect to another host (the file store) is still
verified. No network is used: requests.get is replaced by a fake that records
the keyword arguments of each call.
"""

from unittest import mock

import pytest
import requests

from caltechdata_api.download_from_record import (
    download_content,
    download_files_from_record,
    get_base_url,
    get_files_from_record,
)

LOCAL = "https://127.0.0.1:5000"
STORE = "https://store.example.org/object"
RECORD = "abcde-12345"


class Response:
    def __init__(self, status=200, payload=None, headers=None, body=b""):
        self.status_code = status
        self._payload = payload
        self.headers = headers or {}
        self._body = body

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(str(self.status_code))

    def iter_content(self, chunk_size=1024):
        yield self._body

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


def entries():
    content = f"{LOCAL}/api/records/{RECORD}/files/a.txt/content"
    return {"entries": [{"key": "a.txt", "links": {"content": content}}]}


@pytest.fixture
def calls():
    """Replace requests.get; each call is recorded as (url, kwargs)."""
    seen = []

    def get(url, *args, **kwargs):
        seen.append((url, kwargs))
        if url.endswith("/draft/files"):
            return Response(200, entries())
        if url.endswith("/files"):
            return Response(404)
        if url.endswith("/content"):
            return Response(200, headers={"Location": STORE})
        if url == STORE:
            return Response(200, headers={"content-length": "2"}, body=b"hi")
        raise AssertionError(f"unexpected GET {url}")

    with mock.patch.object(requests, "get", get):
        yield seen


def test_get_base_url_local():
    assert get_base_url(production=False, authors=True, local=True) == LOCAL
    assert get_base_url(production=False, authors=False, local=True) == LOCAL


def test_get_base_url_production_wins_over_local():
    assert get_base_url(production=True, authors=True, local=True) == (
        "https://authors.library.caltech.edu"
    )


def test_get_base_url_unchanged_without_local():
    assert get_base_url(production=False, authors=True) == (
        "https://authors.caltechlibrary.dev"
    )
    assert get_base_url(production=True) == "https://data.caltech.edu"


@pytest.mark.parametrize("verify", [True, False])
def test_get_files_uses_the_local_host_and_verify(calls, verify):
    # the published files are not found, so the draft is tried as well
    files = get_files_from_record(
        RECORD, production=False, authors=True, local=True, token="t", verify=verify
    )
    assert list(files) == ["a.txt"]
    assert [u for u, _ in calls] == [
        f"{LOCAL}/api/records/{RECORD}/files",
        f"{LOCAL}/api/records/{RECORD}/draft/files",
    ]
    for url, kwargs in calls:
        assert kwargs.get("verify", True) is verify, url


@pytest.mark.parametrize("verify", [True, False])
def test_download_verifies_other_hosts(calls, tmp_path, verify):
    download_files_from_record(
        RECORD,
        tmp_path,
        production=False,
        authors=True,
        local=True,
        token="t",
        verify=verify,
    )
    assert (tmp_path / "a.txt").read_bytes() == b"hi"
    by_url = {url: kwargs.get("verify", True) for url, kwargs in calls}
    # the instance's own requests follow verify
    assert by_url[f"{LOCAL}/api/records/{RECORD}/files"] is verify
    assert by_url[f"{LOCAL}/api/records/{RECORD}/files/a.txt/content"] is verify
    # a redirect to another host is always verified
    assert by_url[STORE] is True


def test_download_content_verify_false_stays_on_the_first_host(calls, tmp_path):
    download_content(
        f"{LOCAL}/api/records/{RECORD}/files/a.txt/content",
        tmp_path / "a.txt",
        verify=False,
    )
    by_url = {url: kwargs.get("verify", True) for url, kwargs in calls}
    assert by_url[f"{LOCAL}/api/records/{RECORD}/files/a.txt/content"] is False
    assert by_url[STORE] is True


def test_defaults_are_unchanged(calls):
    get_files_from_record(RECORD, production=False, authors=True, token="t")
    dev = "https://authors.caltechlibrary.dev"
    assert calls[0][0] == f"{dev}/api/records/{RECORD}/files"
    for _, kwargs in calls:
        assert kwargs.get("verify", True) is True
