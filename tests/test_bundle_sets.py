import httpx
import pytest

from hotcodepush import BundleSet, Count, HotCodePushError
from tests.openapi_document import resolve_response_example
from tests.stub_api import StubApi, resolve_sent_json

BUNDLE_SET_ROW = resolve_response_example(method="POST", template="/v1/apps/{appId}/bundle-sets")
BUNDLE_SET_ROW_WITH_RELATIONS = resolve_response_example(
    method="GET", template="/v1/apps/{appId}/bundle-sets/{bundleSetId}"
)
BUNDLE_SETS_URL = "https://api.hotcodepush.com/v1/apps/app/bundle-sets"


def test_counts_the_bundle_sets_of_the_app_filtered_by_number_and_platform() -> None:
    api = StubApi(httpx.Response(200, json={"count": 1}))

    fetched_count = api.client.apps.bundle_sets.count(app_id="app", number=2, platform="ios")

    assert fetched_count == Count(count=1)
    assert api.sent_methods_and_urls == [f"GET {BUNDLE_SETS_URL}/count?number=2&platform=ios"]


def test_posts_the_bundle_ids_of_the_set() -> None:
    api = StubApi(httpx.Response(201, json=BUNDLE_SET_ROW))

    created_bundle_set = api.client.apps.bundle_sets.create(app_id="app", bundle_ids=["bundle"])

    assert created_bundle_set == BundleSet.model_validate(BUNDLE_SET_ROW)
    assert api.sent_methods_and_urls == [f"POST {BUNDLE_SETS_URL}"]
    assert resolve_sent_json(api.last_request) == {"bundleIds": ["bundle"]}


def test_retries_the_creation_when_the_api_is_unavailable() -> None:
    api = StubApi(httpx.Response(503))

    with pytest.raises(HotCodePushError):
        api.client.apps.bundle_sets.create(app_id="app", bundle_ids=["bundle"])

    assert len(api.requests) == 3


def test_gets_the_bundle_set_with_its_bundles() -> None:
    api = StubApi(httpx.Response(200, json=BUNDLE_SET_ROW_WITH_RELATIONS))

    fetched_bundle_set = api.client.apps.bundle_sets.get(
        app_id="app", bundle_set_id="bundle-set", relations=["bundles"]
    )

    assert fetched_bundle_set.bundles is not None
    assert api.sent_methods_and_urls == [f"GET {BUNDLE_SETS_URL}/bundle-set?relations=bundles"]


def test_lists_the_bundle_sets_of_the_app_that_carry_the_bundle_by_number() -> None:
    api = StubApi(httpx.Response(200, json=[BUNDLE_SET_ROW]))

    fetched_bundle_sets = api.client.apps.bundle_sets.list(
        app_id="app", bundle_id="bundle", limit=20, number=2
    )

    assert fetched_bundle_sets == [BundleSet.model_validate(BUNDLE_SET_ROW)]
    assert api.sent_methods_and_urls == [f"GET {BUNDLE_SETS_URL}?bundleId=bundle&limit=20&number=2"]
