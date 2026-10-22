from datetime import date

import httpx

from hotcodepush import UsageStatistics
from tests.openapi_document import resolve_response_example
from tests.stub_api import StubApi

USAGE_STATISTICS = resolve_response_example("GET", "/v1/apps/{appId}/statistics/usage")


def test_gets_the_usage_statistics_of_the_period() -> None:
    api = StubApi(httpx.Response(200, json=USAGE_STATISTICS))

    fetched_statistics = api.client.apps.statistics.usage.get(
        app_id="app", period_since=date(2026, 9, 1), period_until=date(2026, 9, 30)
    )

    assert fetched_statistics == UsageStatistics.model_validate(USAGE_STATISTICS)
    assert api.sent_methods_and_urls == [
        "GET https://api.hotcodepush.com/v1/apps/app/statistics/usage"
        "?periodSince=2026-09-01&periodUntil=2026-09-30"
    ]
