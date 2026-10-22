import httpx

from hotcodepush import UploadedPart
from tests.stub_api import StubApi

SHA256 = "a" * 64


def test_puts_the_part_as_gzip_under_its_number() -> None:
    api = StubApi(httpx.Response(200, json={"etag": "etag", "partNumber": 2}))

    uploaded_part = api.client.apps.files.uploads.parts.upload(
        app_id="app", body=b"part bytes", part_number=2, sha256=SHA256, upload_id="upload"
    )

    assert uploaded_part == UploadedPart(etag="etag", part_number=2)
    assert api.sent_methods_and_urls == [
        f"PUT https://api.hotcodepush.com/v1/apps/app/files/{SHA256}/uploads/upload/parts/2"
    ]
    assert api.last_request.content == b"part bytes"
    assert api.last_request.headers["Content-Type"] == "application/gzip"
