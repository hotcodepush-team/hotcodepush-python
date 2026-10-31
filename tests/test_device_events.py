import httpx

from hotcodepush import Count
from tests.openapi_document import resolve_response_example
from tests.stub_api import StubApi

EVENT_ROWS = resolve_response_example("GET", "/v1/apps/{appId}/devices/{deviceId}/events")
EVENTS_URL = "https://api.hotcodepush.com/v1/apps/app/devices/device/events"


def test_counts_the_events_of_the_device_on_the_release() -> None:
    api = StubApi(httpx.Response(200, json={"count": 2}))

    fetched_count = api.client.apps.devices.events.count(
        app_id="app", device_id="device", release_id="release"
    )

    assert fetched_count == Count(count=2)
    assert api.sent_methods_and_urls == [f"GET {EVENTS_URL}/count?releaseId=release"]


def test_lists_a_page_of_the_events_of_the_device() -> None:
    api = StubApi(httpx.Response(200, json=EVENT_ROWS))

    fetched_events = api.client.apps.devices.events.list(
        app_id="app", device_id="device", limit=100, offset=100
    )

    [fetched_event] = fetched_events
    assert fetched_event.type == "applied"
    assert api.sent_methods_and_urls == [f"GET {EVENTS_URL}?limit=100&offset=100"]


def test_lists_the_events_with_their_releases_when_the_release_relation_is_set() -> None:
    api = StubApi(httpx.Response(200, json=EVENT_ROWS))

    fetched_events = api.client.apps.devices.events.list(
        app_id="app", device_id="device", relations=["release"]
    )

    [fetched_event] = fetched_events
    assert fetched_event.release is not None
    assert api.sent_methods_and_urls == [f"GET {EVENTS_URL}?relations=release"]
