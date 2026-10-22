import httpx

from hotcodepush import Audience
from tests.openapi_document import resolve_response_example
from tests.stub_api import StubApi

AUDIENCE = resolve_response_example("GET", "/v1/apps/{appId}/releases/{releaseId}/audience")


def test_gets_the_audience_the_release_reaches() -> None:
    api = StubApi(httpx.Response(200, json=AUDIENCE))

    fetched_audience = api.client.apps.releases.audience.get(app_id="app", release_id="release")

    assert fetched_audience == Audience.model_validate(AUDIENCE)
    assert api.sent_methods_and_urls == [
        "GET https://api.hotcodepush.com/v1/apps/app/releases/release/audience"
    ]
