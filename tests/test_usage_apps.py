import httpx

from hotcodepush import Count
from tests.openapi_document import resolve_response_example
from tests.stub_api import StubApi

APP_USAGE_MONTH_ROWS = resolve_response_example(
    "GET", "/v1/organizations/{organizationId}/usage/apps"
)
USAGE_APPS_URL = "https://api.hotcodepush.com/v1/organizations/organization/usage/apps"


def test_counts_the_apps_with_usage_in_the_month() -> None:
    api = StubApi(httpx.Response(200, json={"count": 2}))

    fetched_count = api.client.organizations.usage.apps.count(
        month="2026-09", organization_id="organization"
    )

    assert fetched_count == Count(count=2)
    assert api.sent_methods_and_urls == [f"GET {USAGE_APPS_URL}/count?month=2026-09"]


def test_downloads_the_usage_of_the_apps_in_the_month_as_csv() -> None:
    api = StubApi(
        httpx.Response(
            200,
            content=b'"appId","appName"\n',
            headers={"Content-Type": "text/csv; charset=utf-8"},
        )
    )

    downloaded_csv = api.client.organizations.usage.apps.download_csv(
        month="2026-09", organization_id="organization"
    )

    assert downloaded_csv == b'"appId","appName"\n'
    assert api.sent_methods_and_urls == [f"GET {USAGE_APPS_URL}?format=csv&month=2026-09"]


def test_lists_a_page_of_the_usage_of_the_apps_with_their_apps() -> None:
    api = StubApi(httpx.Response(200, json=APP_USAGE_MONTH_ROWS))

    fetched_app_usage_months = api.client.organizations.usage.apps.list(
        limit=10, month="2026-09", offset=10, organization_id="organization", relations=["app"]
    )

    [fetched_app_usage_month] = fetched_app_usage_months
    assert fetched_app_usage_month.app is not None
    assert api.sent_methods_and_urls == [
        f"GET {USAGE_APPS_URL}?limit=10&month=2026-09&offset=10&relations=app"
    ]
