import io

import httpx
import pytest

from hotcodepush import SINGLE_UPLOAD_LIMIT_BYTES, HotCodePushError, UploadedBundlePack
from tests.stub_api import MultipartUploadStubApi, StubApi

BYTES_ABOVE_SINGLE_UPLOAD_LIMIT = bytes(SINGLE_UPLOAD_LIMIT_BYTES + 1)
PACK_URL = "https://api.hotcodepush.com/v1/apps/app/bundles/bundle/pack"
PART_NUMBERS = range(1, 8)


def test_puts_the_pack_as_a_tar() -> None:
    api = StubApi(httpx.Response(200, json={"sizeBytes": 9}))

    uploaded_pack = api.client.apps.bundles.pack.upload(
        app_id="app", body=b"tar bytes", bundle_id="bundle"
    )

    assert uploaded_pack == UploadedBundlePack(size_bytes=9)
    assert api.sent_methods_and_urls == [f"PUT {PACK_URL}"]
    assert api.last_request.content == b"tar bytes"
    assert api.last_request.headers["Content-Type"] == "application/x-tar"


def test_puts_bytes_at_the_single_upload_limit_in_one_request() -> None:
    api = StubApi(httpx.Response(200, json={"sizeBytes": SINGLE_UPLOAD_LIMIT_BYTES}))

    api.client.apps.bundles.pack.upload(
        app_id="app",
        body=BYTES_ABOVE_SINGLE_UPLOAD_LIMIT[:SINGLE_UPLOAD_LIMIT_BYTES],
        bundle_id="bundle",
    )

    assert api.sent_methods_and_urls == [f"PUT {PACK_URL}"]


def test_puts_a_file_object_above_the_single_upload_limit_in_one_request() -> None:
    api = StubApi(httpx.Response(200, json={"sizeBytes": len(BYTES_ABOVE_SINGLE_UPLOAD_LIMIT)}))

    api.client.apps.bundles.pack.upload(
        app_id="app",
        body=io.BytesIO(BYTES_ABOVE_SINGLE_UPLOAD_LIMIT),
        bundle_id="bundle",
        content_length=len(BYTES_ABOVE_SINGLE_UPLOAD_LIMIT),
    )

    assert api.sent_methods_and_urls == [f"PUT {PACK_URL}"]


def test_uploads_bytes_above_the_single_upload_limit_in_parts_and_completes_them() -> None:
    api = MultipartUploadStubApi(completed_body={"sizeBytes": 9})

    uploaded_pack = api.client.apps.bundles.pack.upload(
        app_id="app", body=BYTES_ABOVE_SINGLE_UPLOAD_LIMIT, bundle_id="bundle"
    )

    assert uploaded_pack == UploadedBundlePack(size_bytes=9)
    assert api.sent_methods_and_urls == [
        f"POST {PACK_URL}/uploads",
        *(f"PUT {PACK_URL}/uploads/upload/parts/{part_number}" for part_number in PART_NUMBERS),
        f"POST {PACK_URL}/uploads/upload/complete",
    ]


def test_deletes_the_upload_and_raises_when_a_part_is_refused() -> None:
    api = MultipartUploadStubApi(completed_body={"sizeBytes": 9}, failed_part_number=2)

    with pytest.raises(HotCodePushError) as raised:
        api.client.apps.bundles.pack.upload(
            app_id="app", body=BYTES_ABOVE_SINGLE_UPLOAD_LIMIT, bundle_id="bundle"
        )

    assert raised.value.code == "upload_incomplete"
    assert api.sent_methods_and_urls[-1] == f"DELETE {PACK_URL}/uploads/upload"
