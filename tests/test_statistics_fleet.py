import httpx

from hotcodepush import FleetStatistics
from tests.openapi_document import resolve_response_example
from tests.stub_api import StubApi

FLEET_STATISTICS = resolve_response_example("GET", "/v1/apps/{appId}/statistics/fleet")


def test_gets_the_fleet_statistics_of_the_devices_of_one_channel() -> None:
    api = StubApi(httpx.Response(200, json=FLEET_STATISTICS))

    fetched_statistics = api.client.apps.statistics.fleet.get(app_id="app", channel_id="channel")

    assert fetched_statistics == FleetStatistics.model_validate(FLEET_STATISTICS)
    assert api.sent_methods_and_urls == [
        "GET https://api.hotcodepush.com/v1/apps/app/statistics/fleet?channelId=channel"
    ]
