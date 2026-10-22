import httpx
import pytest

from hotcodepush import App, HotCodePushError
from tests.openapi_document import resolve_response_example
from tests.stub_api import StubApi, resolve_sent_json

APP_ROW = resolve_response_example("GET", "/v1/apps/{appId}")
APP_URL = "https://api.hotcodepush.com/v1/apps/app"


def test_deletes_the_app() -> None:
    api = StubApi(httpx.Response(204))

    api.client.apps.delete(app_id="app")

    assert api.sent_methods_and_urls == [f"DELETE {APP_URL}"]


def test_gets_the_app() -> None:
    api = StubApi(httpx.Response(200, json=APP_ROW))

    fetched_app = api.client.apps.get(app_id="app")

    assert fetched_app == App.model_validate(APP_ROW)
    assert api.sent_methods_and_urls == [f"GET {APP_URL}"]


def test_posts_the_target_organization_to_transfer_the_app() -> None:
    api = StubApi(httpx.Response(200, json=APP_ROW))

    api.client.apps.transfer(app_id="app", organization_id="organization")

    assert api.sent_methods_and_urls == [f"POST {APP_URL}/transfer"]
    assert resolve_sent_json(api.last_request) == {"organizationId": "organization"}


def test_does_not_retry_the_transfer_when_the_api_is_unavailable() -> None:
    api = StubApi(httpx.Response(503))

    with pytest.raises(HotCodePushError):
        api.client.apps.transfer(app_id="app", organization_id="organization")

    assert len(api.requests) == 1


def test_patches_the_app() -> None:
    api = StubApi(httpx.Response(200, json=APP_ROW))

    api.client.apps.update(app_id="app", channel_link_template="demo://channels/{channelId}")

    assert api.sent_methods_and_urls == [f"PATCH {APP_URL}"]
    assert resolve_sent_json(api.last_request) == {
        "channelLinkTemplate": "demo://channels/{channelId}"
    }


def test_patches_the_deep_link_template_to_null_when_it_is_cleared() -> None:
    api = StubApi(httpx.Response(200, json=APP_ROW))

    api.client.apps.update(app_id="app", channel_link_template=None)

    assert resolve_sent_json(api.last_request) == {"channelLinkTemplate": None}
