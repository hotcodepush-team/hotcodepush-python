import httpx

from hotcodepush import Binary, Count, ManifestFile
from tests.openapi_document import resolve_response_example
from tests.stub_api import StubApi, resolve_sent_json

BINARIES_URL = "https://api.hotcodepush.com/v1/apps/app/binaries"
BINARY_ROW = resolve_response_example("GET", "/v1/apps/{appId}/binaries/{binaryId}")
FINGERPRINT = f"fp1:{'a' * 64}"


def test_counts_the_binaries_of_the_app_filtered_by_fingerprint_and_platform() -> None:
    api = StubApi(httpx.Response(200, json={"count": 3}))

    fetched_count = api.client.apps.binaries.count(
        app_id="app", fingerprint=FINGERPRINT, platform="ios"
    )

    assert fetched_count == Count(count=3)
    assert api.sent_methods_and_urls == [
        f"GET {BINARIES_URL}/count?fingerprint=fp1%3A{'a' * 64}&platform=ios"
    ]


def test_posts_the_binary_identity_with_force_and_its_idempotency_key() -> None:
    api = StubApi(httpx.Response(201, json=BINARY_ROW))

    created_binary = api.client.apps.binaries.create(
        app_id="app",
        build="42",
        files=[ManifestFile(path="index.html", sha256="a" * 64, size_bytes=5)],
        force=True,
        idempotency_key="key",
        platform="android",
        version="1.0.0",
    )

    assert created_binary == Binary.model_validate(BINARY_ROW)
    assert api.sent_methods_and_urls == [f"POST {BINARIES_URL}"]
    assert api.last_request.headers["Idempotency-Key"] == "key"
    assert resolve_sent_json(api.last_request) == {
        "build": "42",
        "files": [{"path": "index.html", "sha256": "a" * 64, "sizeBytes": 5}],
        "force": True,
        "platform": "android",
        "version": "1.0.0",
    }


def test_gets_the_binary() -> None:
    api = StubApi(httpx.Response(200, json=BINARY_ROW))

    fetched_binary = api.client.apps.binaries.get(app_id="app", binary_id="binary")

    assert fetched_binary == Binary.model_validate(BINARY_ROW)
    assert api.sent_methods_and_urls == [f"GET {BINARIES_URL}/binary"]


def test_lists_the_binaries_of_the_app_filtered_by_fingerprint_and_platform() -> None:
    api = StubApi(httpx.Response(200, json=[BINARY_ROW]))

    fetched_binaries = api.client.apps.binaries.list(
        app_id="app", fingerprint=FINGERPRINT, limit=20, platform="android"
    )

    assert fetched_binaries == [Binary.model_validate(BINARY_ROW)]
    assert api.sent_methods_and_urls == [
        f"GET {BINARIES_URL}?fingerprint=fp1%3A{'a' * 64}&limit=20&platform=android"
    ]
