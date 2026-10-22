import httpx

from hotcodepush import UploadedPart
from tests.stub_api import StubApi


def test_puts_the_part_as_a_tar_under_its_number() -> None:
    api = StubApi(httpx.Response(200, json={"etag": "etag", "partNumber": 2}))

    uploaded_part = api.client.apps.bundles.pack.uploads.parts.upload(
        app_id="app", body=b"part bytes", bundle_id="bundle", part_number=2, upload_id="upload"
    )

    assert uploaded_part == UploadedPart(etag="etag", part_number=2)
    assert api.sent_methods_and_urls == [
        "PUT https://api.hotcodepush.com/v1/apps/app/bundles/bundle/pack/uploads/upload/parts/2"
    ]
    assert api.last_request.content == b"part bytes"
    assert api.last_request.headers["Content-Type"] == "application/x-tar"
