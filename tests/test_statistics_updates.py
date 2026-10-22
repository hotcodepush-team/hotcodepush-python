from datetime import date

import httpx

from hotcodepush import UpdateStatistics
from tests.openapi_document import resolve_response_example
from tests.stub_api import StubApi

UPDATE_STATISTICS = resolve_response_example("GET", "/v1/apps/{appId}/statistics/updates")


def test_gets_the_update_statistics_of_one_channel_and_release_over_the_period() -> None:
    api = StubApi(httpx.Response(200, json=UPDATE_STATISTICS))

    fetched_statistics = api.client.apps.statistics.updates.get(
        app_id="app",
        channel_id="channel",
        period_since=date(2026, 9, 1),
        period_until=date(2026, 9, 30),
        release_id="release",
    )

    assert fetched_statistics == UpdateStatistics.model_validate(UPDATE_STATISTICS)
    assert api.sent_methods_and_urls == [
        "GET https://api.hotcodepush.com/v1/apps/app/statistics/updates"
        "?channelId=channel&periodSince=2026-09-01&periodUntil=2026-09-30&releaseId=release"
    ]
