import httpx
import pytest

from hotcodepush import Bundle, BundleSignature, Count, HotCodePushError, ManifestFile
from tests.openapi_document import resolve_response_example
from tests.stub_api import StubApi, resolve_sent_json

BUNDLE_ROW = resolve_response_example("GET", "/v1/apps/{appId}/bundles/{bundleId}")
BUNDLES_URL = "https://api.hotcodepush.com/v1/apps/app/bundles"
FINGERPRINT = f"fp1:{'a' * 64}"


def test_posts_to_complete_the_bundle() -> None:
    api = StubApi(httpx.Response(200, json=BUNDLE_ROW))

    completed_bundle = api.client.apps.bundles.complete(app_id="app", bundle_id="bundle")

    assert completed_bundle == Bundle.model_validate(BUNDLE_ROW)
    assert api.sent_methods_and_urls == [f"POST {BUNDLES_URL}/bundle/complete"]
    assert api.last_request.content == b""


def test_retries_the_completion_when_the_api_is_unavailable() -> None:
    api = StubApi(httpx.Response(503))

    with pytest.raises(HotCodePushError):
        api.client.apps.bundles.complete(app_id="app", bundle_id="bundle")

    assert len(api.requests) == 3


def test_counts_the_bundles_of_the_app_filtered_by_use_and_platform() -> None:
    api = StubApi(httpx.Response(200, json={"count": 3}))

    fetched_count = api.client.apps.bundles.count(app_id="app", is_in_use=True, platform="ios")

    assert fetched_count == Count(count=3)
    assert api.sent_methods_and_urls == [f"GET {BUNDLES_URL}/count?isInUse=true&platform=ios"]


def test_posts_the_manifest_with_its_idempotency_key() -> None:
    api = StubApi(httpx.Response(201, json=BUNDLE_ROW))

    created_bundle = api.client.apps.bundles.create(
        app_id="app",
        files=[ManifestFile(path="index.html", sha256="a" * 64, size_bytes=5)],
        idempotency_key="key",
        platforms=["android", "ios"],
        signature=BundleSignature(key_id="key", value="signature"),
        version="1.0.0",
    )

    assert created_bundle == Bundle.model_validate(BUNDLE_ROW)
    assert api.sent_methods_and_urls == [f"POST {BUNDLES_URL}"]
    assert api.last_request.headers["Idempotency-Key"] == "key"
    assert resolve_sent_json(api.last_request) == {
        "files": [{"path": "index.html", "sha256": "a" * 64, "sizeBytes": 5}],
        "platforms": ["android", "ios"],
        "signature": {"keyId": "key", "value": "signature"},
        "version": "1.0.0",
    }


def test_deletes_the_bundle() -> None:
    api = StubApi(httpx.Response(204))

    api.client.apps.bundles.delete(app_id="app", bundle_id="bundle")

    assert api.sent_methods_and_urls == [f"DELETE {BUNDLES_URL}/bundle"]


def test_gets_the_bundle() -> None:
    api = StubApi(httpx.Response(200, json=BUNDLE_ROW))

    fetched_bundle = api.client.apps.bundles.get(app_id="app", bundle_id="bundle")

    assert fetched_bundle == Bundle.model_validate(BUNDLE_ROW)
    assert api.sent_methods_and_urls == [f"GET {BUNDLES_URL}/bundle"]


def test_lists_the_bundles_of_the_app_filtered_by_fingerprint_use_platform_and_source() -> None:
    api = StubApi(httpx.Response(200, json=[BUNDLE_ROW]))

    fetched_bundles = api.client.apps.bundles.list(
        app_id="app", fingerprint=FINGERPRINT, is_in_use=False, platform="ios", source="upload"
    )

    assert fetched_bundles == [Bundle.model_validate(BUNDLE_ROW)]
    assert api.sent_methods_and_urls == [
        f"GET {BUNDLES_URL}?fingerprint=fp1%3A{'a' * 64}&isInUse=false&platform=ios&source=upload"
    ]
