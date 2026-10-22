import httpx

from hotcodepush import Count
from tests.openapi_document import resolve_response_example
from tests.stub_api import StubApi

DELTA_ROWS_WITH_BASE_BUNDLES = resolve_response_example(
    "GET", "/v1/apps/{appId}/bundles/{bundleId}/deltas"
)
DELTAS_URL = "https://api.hotcodepush.com/v1/apps/app/bundles/bundle/deltas"


def test_counts_the_delta_packs_of_the_bundle() -> None:
    api = StubApi(httpx.Response(200, json={"count": 2}))

    fetched_count = api.client.apps.bundles.deltas.count(app_id="app", bundle_id="bundle")

    assert fetched_count == Count(count=2)
    assert api.sent_methods_and_urls == [f"GET {DELTAS_URL}/count"]


def test_lists_the_delta_packs_of_the_bundle_with_their_base_bundles() -> None:
    api = StubApi(httpx.Response(200, json=DELTA_ROWS_WITH_BASE_BUNDLES))

    fetched_delta_packs = api.client.apps.bundles.deltas.list(
        app_id="app", bundle_id="bundle", relations=["baseBundle"]
    )

    [fetched_delta_pack] = fetched_delta_packs
    assert fetched_delta_pack.base_bundle is not None
    assert api.sent_methods_and_urls == [f"GET {DELTAS_URL}?relations=baseBundle"]
