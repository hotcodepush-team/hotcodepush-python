import httpx

from hotcodepush import Count
from tests.openapi_document import resolve_response_example
from tests.stub_api import StubApi

FILE_ROWS = resolve_response_example("GET", "/v1/apps/{appId}/bundles/{bundleId}/files")
FILES_URL = "https://api.hotcodepush.com/v1/apps/app/bundles/bundle/files"


def test_counts_the_files_of_the_bundle_still_to_upload() -> None:
    api = StubApi(httpx.Response(200, json={"count": 3}))

    fetched_count = api.client.apps.bundles.files.count(
        app_id="app", bundle_id="bundle", is_stored=False
    )

    assert fetched_count == Count(count=3)
    assert api.sent_methods_and_urls == [f"GET {FILES_URL}/count?isStored=false"]


def test_lists_a_page_of_the_files_of_the_bundle_still_to_upload() -> None:
    api = StubApi(httpx.Response(200, json=FILE_ROWS))

    fetched_files = api.client.apps.bundles.files.list(
        app_id="app", bundle_id="bundle", is_stored=False, limit=100, offset=100
    )

    [fetched_file] = fetched_files
    assert fetched_file.stored_at is not None
    assert api.sent_methods_and_urls == [f"GET {FILES_URL}?isStored=false&limit=100&offset=100"]
