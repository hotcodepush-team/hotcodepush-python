import httpx

from hotcodepush import Audience
from tests.openapi_document import resolve_response_example
from tests.stub_api import StubApi

AUDIENCE = resolve_response_example("GET", "/v1/apps/{appId}/channels/{channelId}/audience")


def test_gets_the_audience_with_each_condition_repeated() -> None:
    api = StubApi(httpx.Response(200, json=AUDIENCE))

    fetched_audience = api.client.apps.channels.audience.get(
        app_id="app", binary=[">=2.0.0", "<3.0.0"], channel_id="channel", rollout_percent=10
    )

    assert fetched_audience == Audience.model_validate(AUDIENCE)
    assert api.sent_methods_and_urls == [
        "GET https://api.hotcodepush.com/v1/apps/app/channels/channel/audience"
        "?binary=%3E%3D2.0.0&binary=%3C3.0.0&rolloutPercent=10"
    ]
