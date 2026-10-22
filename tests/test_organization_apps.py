import httpx

from hotcodepush import App, Count
from tests.openapi_document import resolve_response_example
from tests.stub_api import StubApi, resolve_sent_json

APP_ROW = resolve_response_example("GET", "/v1/apps/{appId}")
APPS_URL = "https://api.hotcodepush.com/v1/organizations/organization/apps"


def test_counts_the_apps_of_the_organization_under_the_query() -> None:
    api = StubApi(httpx.Response(200, json={"count": 3}))

    fetched_count = api.client.organizations.apps.count(
        organization_id="organization", query="demo"
    )

    assert fetched_count == Count(count=3)
    assert api.sent_methods_and_urls == [f"GET {APPS_URL}/count?query=demo"]


def test_posts_the_app_to_its_organization_with_its_idempotency_key() -> None:
    api = StubApi(httpx.Response(201, json=APP_ROW))

    created_app = api.client.organizations.apps.create(
        framework="capacitor", idempotency_key="key", name="Demo", organization_id="organization"
    )

    assert created_app == App.model_validate(APP_ROW)
    assert api.sent_methods_and_urls == [f"POST {APPS_URL}"]
    assert api.last_request.headers["Idempotency-Key"] == "key"
    assert resolve_sent_json(api.last_request) == {"framework": "capacitor", "name": "Demo"}


def test_lists_the_apps_of_the_organization() -> None:
    api = StubApi(httpx.Response(200, json=[APP_ROW]))

    fetched_apps = api.client.organizations.apps.list(offset=50, organization_id="organization")

    assert fetched_apps == [App.model_validate(APP_ROW)]
    assert api.sent_methods_and_urls == [f"GET {APPS_URL}?offset=50"]
