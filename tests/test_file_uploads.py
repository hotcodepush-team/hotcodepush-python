import httpx

from hotcodepush import AppFile, MultipartUpload, UploadedPart
from tests.openapi_document import resolve_response_example
from tests.stub_api import StubApi, resolve_sent_json

FILE_ROW = resolve_response_example(
    "POST", "/v1/apps/{appId}/files/{sha256}/uploads/{uploadId}/complete"
)
SHA256 = "a" * 64
UPLOADS_URL = f"https://api.hotcodepush.com/v1/apps/app/files/{SHA256}/uploads"


def test_posts_the_parts_to_complete_the_upload() -> None:
    api = StubApi(httpx.Response(201, json=FILE_ROW))

    completed_file = api.client.apps.files.uploads.complete(
        app_id="app",
        parts=[UploadedPart(etag="etag", part_number=1)],
        sha256=SHA256,
        upload_id="upload",
    )

    assert completed_file == AppFile.model_validate(FILE_ROW)
    assert api.sent_methods_and_urls == [f"POST {UPLOADS_URL}/upload/complete"]
    assert resolve_sent_json(api.last_request) == {"parts": [{"etag": "etag", "partNumber": 1}]}


def test_retries_the_completion_when_the_api_answers_502() -> None:
    api = StubApi(httpx.Response(502), httpx.Response(200, json=FILE_ROW))

    completed_file = api.client.apps.files.uploads.complete(
        app_id="app",
        parts=[UploadedPart(etag="etag", part_number=1)],
        sha256=SHA256,
        upload_id="upload",
    )

    assert completed_file == AppFile.model_validate(FILE_ROW)
    assert len(api.requests) == 2


def test_posts_to_start_the_upload_without_an_idempotency_key() -> None:
    api = StubApi(httpx.Response(201, json={"uploadId": "upload"}))

    created_upload = api.client.apps.files.uploads.create(app_id="app", sha256=SHA256)

    assert created_upload == MultipartUpload(upload_id="upload")
    assert api.sent_methods_and_urls == [f"POST {UPLOADS_URL}"]
    assert api.last_request.content == b""
    assert "Idempotency-Key" not in api.last_request.headers


def test_retries_the_start_when_the_api_answers_502() -> None:
    api = StubApi(httpx.Response(502), httpx.Response(201, json={"uploadId": "upload"}))

    created_upload = api.client.apps.files.uploads.create(app_id="app", sha256=SHA256)

    assert created_upload == MultipartUpload(upload_id="upload")
    assert len(api.requests) == 2


def test_deletes_the_upload_to_abort_it() -> None:
    api = StubApi(httpx.Response(204))

    api.client.apps.files.uploads.delete(app_id="app", sha256=SHA256, upload_id="upload")

    assert api.sent_methods_and_urls == [f"DELETE {UPLOADS_URL}/upload"]
