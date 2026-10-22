import httpx
import pytest

from hotcodepush import HotCodePushError, MultipartUpload, UploadedBundlePack, UploadedPart
from tests.stub_api import StubApi, resolve_sent_json

UPLOADS_URL = "https://api.hotcodepush.com/v1/apps/app/bundles/bundle/pack/uploads"


def test_posts_the_parts_to_complete_the_upload() -> None:
    api = StubApi(httpx.Response(200, json={"sizeBytes": 9}))

    completed_pack = api.client.apps.bundles.pack.uploads.complete(
        app_id="app",
        bundle_id="bundle",
        parts=[UploadedPart(etag="etag", part_number=1)],
        upload_id="upload",
    )

    assert completed_pack == UploadedBundlePack(size_bytes=9)
    assert api.sent_methods_and_urls == [f"POST {UPLOADS_URL}/upload/complete"]
    assert resolve_sent_json(api.last_request) == {"parts": [{"etag": "etag", "partNumber": 1}]}


def test_does_not_retry_the_completion_when_the_api_is_unavailable() -> None:
    api = StubApi(httpx.Response(503))

    with pytest.raises(HotCodePushError):
        api.client.apps.bundles.pack.uploads.complete(
            app_id="app",
            bundle_id="bundle",
            parts=[UploadedPart(etag="etag", part_number=1)],
            upload_id="upload",
        )

    assert len(api.requests) == 1


def test_posts_to_start_the_upload_without_an_idempotency_key() -> None:
    api = StubApi(httpx.Response(201, json={"uploadId": "upload"}))

    created_upload = api.client.apps.bundles.pack.uploads.create(app_id="app", bundle_id="bundle")

    assert created_upload == MultipartUpload(upload_id="upload")
    assert api.sent_methods_and_urls == [f"POST {UPLOADS_URL}"]
    assert api.last_request.content == b""
    assert "Idempotency-Key" not in api.last_request.headers


def test_retries_the_start_when_the_api_answers_502() -> None:
    api = StubApi(httpx.Response(502), httpx.Response(201, json={"uploadId": "upload"}))

    created_upload = api.client.apps.bundles.pack.uploads.create(app_id="app", bundle_id="bundle")

    assert created_upload == MultipartUpload(upload_id="upload")
    assert len(api.requests) == 2


def test_deletes_the_upload_to_abort_it() -> None:
    api = StubApi(httpx.Response(204))

    api.client.apps.bundles.pack.uploads.delete(
        app_id="app", bundle_id="bundle", upload_id="upload"
    )

    assert api.sent_methods_and_urls == [f"DELETE {UPLOADS_URL}/upload"]
