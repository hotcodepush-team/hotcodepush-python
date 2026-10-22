import httpx

from hotcodepush import Count, Device
from tests.openapi_document import resolve_response_example
from tests.stub_api import StubApi

DEVICE_ROW = resolve_response_example("GET", "/v1/apps/{appId}/devices/{deviceId}")
DEVICES_URL = "https://api.hotcodepush.com/v1/apps/app/devices"


def test_counts_the_devices_under_the_filters() -> None:
    api = StubApi(httpx.Response(200, json={"count": 7}))

    fetched_count = api.client.apps.devices.count(
        app_id="app", binary_version="2.4.1", platform="ios"
    )

    assert fetched_count == Count(count=7)
    assert api.sent_methods_and_urls == [
        f"GET {DEVICES_URL}/count?binaryVersion=2.4.1&platform=ios"
    ]


def test_deletes_the_device() -> None:
    api = StubApi(httpx.Response(204))

    api.client.apps.devices.delete(app_id="app", device_id="device")

    assert api.sent_methods_and_urls == [f"DELETE {DEVICES_URL}/device"]


def test_deletes_the_devices_named_by_the_ids() -> None:
    api = StubApi(httpx.Response(204))

    api.client.apps.devices.delete_many(app_id="app", ids=["first", "second"])

    assert api.sent_methods_and_urls == [f"DELETE {DEVICES_URL}?ids=first%2Csecond"]


def test_gets_the_device_with_its_channel() -> None:
    api = StubApi(httpx.Response(200, json=DEVICE_ROW))

    fetched_device = api.client.apps.devices.get(
        app_id="app", device_id="device", relations=["channel"]
    )

    assert fetched_device == Device.model_validate(DEVICE_ROW)
    assert fetched_device.channel is not None
    assert api.sent_methods_and_urls == [f"GET {DEVICES_URL}/device?relations=channel"]


def test_lists_the_devices_with_an_attribute_filter() -> None:
    api = StubApi(httpx.Response(200, json=[DEVICE_ROW]))

    fetched_devices = api.client.apps.devices.list(app_id="app", attribute="userId=42", limit=20)

    assert fetched_devices == [Device.model_validate(DEVICE_ROW)]
    assert api.sent_methods_and_urls == [f"GET {DEVICES_URL}?attribute=userId%3D42&limit=20"]
