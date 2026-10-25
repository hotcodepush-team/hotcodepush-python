import io

import httpx
import pytest

from hotcodepush import PART_SIZE_BYTES, SINGLE_UPLOAD_LIMIT_BYTES, AppFile, HotCodePushError
from tests.openapi_document import resolve_response_example
from tests.stub_api import MultipartUploadStubApi, StubApi, resolve_sent_json

BYTES_ABOVE_SINGLE_UPLOAD_LIMIT = bytes(SINGLE_UPLOAD_LIMIT_BYTES + 1)
FILE_ROW = resolve_response_example("PUT", "/v1/apps/{appId}/files/{sha256}")
SHA256 = "a" * 64
FILE_URL = f"https://api.hotcodepush.com/v1/apps/app/files/{SHA256}"
PART_NUMBERS = range(1, 8)


def test_puts_the_gzip_file_object_with_its_content_length() -> None:
    api = StubApi(httpx.Response(201, json=FILE_ROW))

    uploaded_file = api.client.apps.files.upload(
        app_id="app", body=io.BytesIO(b"gzip bytes"), content_length=10, sha256=SHA256
    )

    assert uploaded_file == AppFile.model_validate(FILE_ROW)
    assert api.sent_methods_and_urls == [f"PUT {FILE_URL}"]
    assert api.last_request.content == b"gzip bytes"
    assert api.last_request.headers["Content-Length"] == "10"
    assert api.last_request.headers["Content-Type"] == "application/gzip"


def test_puts_bytes_at_the_single_upload_limit_in_one_request() -> None:
    api = StubApi(httpx.Response(201, json=FILE_ROW))

    api.client.apps.files.upload(
        app_id="app",
        body=BYTES_ABOVE_SINGLE_UPLOAD_LIMIT[:SINGLE_UPLOAD_LIMIT_BYTES],
        sha256=SHA256,
    )

    assert api.sent_methods_and_urls == [f"PUT {FILE_URL}"]


def test_uploads_bytes_above_the_single_upload_limit_in_parts_and_completes_them() -> None:
    api = MultipartUploadStubApi(completed_body=FILE_ROW)

    uploaded_file = api.client.apps.files.upload(
        app_id="app", body=BYTES_ABOVE_SINGLE_UPLOAD_LIMIT, sha256=SHA256
    )

    assert uploaded_file == AppFile.model_validate(FILE_ROW)
    assert api.sent_methods_and_urls == [
        f"POST {FILE_URL}/uploads",
        *(f"PUT {FILE_URL}/uploads/upload/parts/{part_number}" for part_number in PART_NUMBERS),
        f"POST {FILE_URL}/uploads/upload/complete",
    ]
    assert [len(request.content) for request in api.requests[1:-1]] == [
        *[PART_SIZE_BYTES] * 6,
        SINGLE_UPLOAD_LIMIT_BYTES + 1 - 6 * PART_SIZE_BYTES,
    ]
    assert resolve_sent_json(api.last_request) == {
        "parts": [
            {"etag": f"etag-{part_number}", "partNumber": part_number}
            for part_number in PART_NUMBERS
        ]
    }


def test_deletes_the_upload_and_raises_when_a_part_is_refused() -> None:
    api = MultipartUploadStubApi(completed_body=FILE_ROW, failed_part_number=2)

    with pytest.raises(HotCodePushError) as raised:
        api.client.apps.files.upload(
            app_id="app", body=BYTES_ABOVE_SINGLE_UPLOAD_LIMIT, sha256=SHA256
        )

    assert (raised.value.code, raised.value.status) == ("upload_incomplete", 409)
    assert api.sent_methods_and_urls == [
        f"POST {FILE_URL}/uploads",
        f"PUT {FILE_URL}/uploads/upload/parts/1",
        f"PUT {FILE_URL}/uploads/upload/parts/2",
        f"DELETE {FILE_URL}/uploads/upload",
    ]
