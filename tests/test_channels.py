from datetime import UTC, datetime

import httpx
import pytest

from hotcodepush import Channel, Count, HotCodePushError
from tests.openapi_document import resolve_response_example
from tests.stub_api import StubApi, resolve_sent_json

CHANNEL_ROW = resolve_response_example("GET", "/v1/apps/{appId}/channels/{channelId}")
CHANNELS_URL = "https://api.hotcodepush.com/v1/apps/app/channels"


def test_counts_the_channels_of_the_app_under_the_query() -> None:
    api = StubApi(httpx.Response(200, json={"count": 3}))

    fetched_count = api.client.apps.channels.count(app_id="app", query="stag")

    assert fetched_count == Count(count=3)
    assert api.sent_methods_and_urls == [f"GET {CHANNELS_URL}/count?query=stag"]


def test_posts_the_channel_to_its_app_with_its_idempotency_key() -> None:
    api = StubApi(httpx.Response(201, json=CHANNEL_ROW))

    created_channel = api.client.apps.channels.create(
        app_id="app",
        expires_at=datetime(2026, 11, 1, tzinfo=UTC),
        idempotency_key="key",
        is_protected=True,
        name="staging",
    )

    assert created_channel == Channel.model_validate(CHANNEL_ROW)
    assert api.sent_methods_and_urls == [f"POST {CHANNELS_URL}"]
    assert api.last_request.headers["Idempotency-Key"] == "key"
    assert resolve_sent_json(api.last_request) == {
        "expiresAt": "2026-11-01T00:00:00.000Z",
        "isProtected": True,
        "name": "staging",
    }


def test_deletes_the_channel() -> None:
    api = StubApi(httpx.Response(204))

    api.client.apps.channels.delete(app_id="app", channel_id="channel")

    assert api.sent_methods_and_urls == [f"DELETE {CHANNELS_URL}/channel"]


def test_deletes_the_channels_named_by_the_ids() -> None:
    api = StubApi(httpx.Response(204))

    api.client.apps.channels.delete_many(app_id="app", ids=["first", "second"])

    assert api.sent_methods_and_urls == [f"DELETE {CHANNELS_URL}?ids=first%2Csecond"]


def test_gets_the_channel() -> None:
    api = StubApi(httpx.Response(200, json=CHANNEL_ROW))

    fetched_channel = api.client.apps.channels.get(app_id="app", channel_id="channel")

    assert fetched_channel == Channel.model_validate(CHANNEL_ROW)
    assert api.sent_methods_and_urls == [f"GET {CHANNELS_URL}/channel"]


def test_lists_the_channels_of_the_app() -> None:
    api = StubApi(httpx.Response(200, json=[CHANNEL_ROW]))

    fetched_channels = api.client.apps.channels.list(app_id="app", limit=100)

    assert fetched_channels == [Channel.model_validate(CHANNEL_ROW)]
    assert api.sent_methods_and_urls == [f"GET {CHANNELS_URL}?limit=100"]


def test_posts_to_pause_the_channel() -> None:
    api = StubApi(httpx.Response(200, json=CHANNEL_ROW))

    api.client.apps.channels.pause(app_id="app", channel_id="channel")

    assert api.sent_methods_and_urls == [f"POST {CHANNELS_URL}/channel/pause"]
    assert api.last_request.content == b""


def test_retries_the_pause_when_the_api_is_unavailable() -> None:
    api = StubApi(httpx.Response(503))

    with pytest.raises(HotCodePushError):
        api.client.apps.channels.pause(app_id="app", channel_id="channel")

    assert len(api.requests) == 3


def test_posts_to_resume_the_channel() -> None:
    api = StubApi(httpx.Response(200, json=CHANNEL_ROW))

    api.client.apps.channels.resume(app_id="app", channel_id="channel")

    assert api.sent_methods_and_urls == [f"POST {CHANNELS_URL}/channel/resume"]
    assert api.last_request.content == b""


def test_retries_the_resume_when_the_api_is_unavailable() -> None:
    api = StubApi(httpx.Response(503))

    with pytest.raises(HotCodePushError):
        api.client.apps.channels.resume(app_id="app", channel_id="channel")

    assert len(api.requests) == 3


def test_patches_the_channel() -> None:
    api = StubApi(httpx.Response(200, json=CHANNEL_ROW))

    api.client.apps.channels.update(app_id="app", channel_id="channel", is_discoverable=True)

    assert api.sent_methods_and_urls == [f"PATCH {CHANNELS_URL}/channel"]
    assert resolve_sent_json(api.last_request) == {"isDiscoverable": True}


def test_patches_the_expiry_to_null_when_it_is_cleared() -> None:
    api = StubApi(httpx.Response(200, json=CHANNEL_ROW))

    api.client.apps.channels.update(app_id="app", channel_id="channel", expires_at=None)

    assert resolve_sent_json(api.last_request) == {"expiresAt": None}
