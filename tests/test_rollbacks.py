import httpx

from hotcodepush import Release
from tests.openapi_document import resolve_response_example
from tests.stub_api import StubApi, resolve_sent_json

RELEASE_ROW = resolve_response_example("POST", "/v1/apps/{appId}/channels/{channelId}/rollbacks")


def test_posts_the_rollback_to_its_channel_with_its_idempotency_key() -> None:
    api = StubApi(httpx.Response(201, json=RELEASE_ROW))

    created_release = api.client.apps.channels.rollbacks.create(
        app_id="app",
        channel_id="channel",
        idempotency_key="key",
        is_mandatory=False,
        to_release_id="target",
    )

    assert created_release == Release.model_validate(RELEASE_ROW)
    assert api.sent_methods_and_urls == [
        "POST https://api.hotcodepush.com/v1/apps/app/channels/channel/rollbacks"
    ]
    assert api.last_request.headers["Idempotency-Key"] == "key"
    assert resolve_sent_json(api.last_request) == {"isMandatory": False, "toReleaseId": "target"}
