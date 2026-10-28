"""caltechdata_edit passes its verify argument to every request it makes.

A test instance with a self-signed certificate (local=True) needs verify=False
on every call, including the ones made by write_files_rdm and add_file_links.
No network is used: requests is replaced by a router that answers the calls an
edit of a published record makes, and records the keyword arguments.
"""

from types import SimpleNamespace
from unittest import mock
from urllib.parse import urlsplit

import pytest
import requests

from caltechdata_api import caltechdata_edit

BASE = "https://127.0.0.1:5000"
RECORD = "abcde-12345"
NEW = "fghij-67890"


def respond(method, url):
    """Return (status, payload) for the calls an edit makes."""
    path = urlsplit(url).path
    if method == "GET":
        if path.endswith("/draft/files"):
            return 200, {"entries": []}
        if path.endswith("/draft"):
            return 200, {}
        return 200, {"status": "published", "files": {"enabled": False}}
    if method == "POST":
        if path.endswith("/versions"):
            return 201, {"id": NEW}
        if path.endswith("/draft/files"):
            link = f"{BASE}/api/records/{NEW}/draft/files/a.txt"
            return 201, {
                "entries": [
                    {
                        "key": "a.txt",
                        "links": {
                            "self": link,
                            "content": link + "/content",
                            "commit": link + "/commit",
                        },
                    }
                ]
            }
        if path.endswith("/commit"):
            return 200, {}
        if path.endswith("/actions/publish"):
            return 202, {"id": NEW, "pids": {"doi": {"identifier": "10.1/x"}}}
    if method == "PUT":
        if path.endswith("/content"):
            return 200, {}
        return 200, {"links": {"files": f"{BASE}/api/records/{NEW}/draft/files"}}
    raise AssertionError(f"unexpected {method} {url}")


@pytest.fixture
def calls():
    """Replace requests.get/post/put/delete; the list records (method, kwargs)."""
    seen = []

    def make(method):
        def fake(url, *args, **kwargs):
            seen.append((method, url, kwargs))
            status, payload = respond(method, url)
            return SimpleNamespace(
                status_code=status, json=lambda: payload, text=str(payload), url=url
            )

        return fake

    with mock.patch.multiple(
        requests, **{m.lower(): make(m) for m in ("GET", "POST", "PUT", "DELETE")}
    ):
        yield seen


@pytest.fixture
def s3():
    """Stand in for s3fs, which add_file_links uses to size each linked file."""
    fs = mock.Mock()
    fs.return_value.info.return_value = {"size": 1}
    with mock.patch("caltechdata_api.caltechdata_write.s3fs.S3FileSystem", fs):
        yield fs


def edit(**kwargs):
    return caltechdata_edit(
        RECORD, token="t", authors=True, local=True, publish=True, **kwargs
    )


def assert_all(calls, expected):
    assert calls, "no requests were made"
    for method, url, kwargs in calls:
        assert (
            kwargs.get("verify", True) is expected
        ), f"{method} {url} did not get verify={expected}"


@pytest.mark.parametrize("verify", [True, False])
def test_metadata_only_edit(calls, verify):
    edit(verify=verify)
    assert_all(calls, verify)


@pytest.mark.parametrize("verify", [True, False])
def test_new_version(calls, verify):
    edit(new_version=True, verify=verify)
    assert_all(calls, verify)


@pytest.mark.parametrize("verify", [True, False])
def test_file_upload(calls, tmp_path, verify):
    path = tmp_path / "a.txt"
    path.write_text("x")
    edit(files=[str(path)], verify=verify)
    assert_all(calls, verify)
    # the upload and its commit were part of the run
    assert any(m == "PUT" and u.endswith("/content") for m, u, _ in calls)


@pytest.mark.parametrize("verify", [True, False])
def test_file_links(calls, s3, verify):
    edit(file_links=["https://s3.example.org/bucket/a.txt"], verify=verify)
    assert_all(calls, verify)
    assert any(m == "POST" and u.endswith("/draft/files") for m, u, _ in calls)


def test_verify_defaults_to_true(calls):
    edit()
    assert_all(calls, True)
    assert all(kwargs.get("verify", True) is True for _, _, kwargs in calls)
