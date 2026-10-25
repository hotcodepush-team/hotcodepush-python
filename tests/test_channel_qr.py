import httpx
import pytest

from hotcodepush import HotCodePushError
from tests.stub_api import StubApi

QR_URL = "https://api.hotcodepush.com/v1/apps/app/channels/channel/qr"


def test_gets_the_qr_image_of_the_channel_in_the_given_format() -> None:
    api = StubApi(httpx.Response(200, content=b"png", headers={"Content-Type": "image/png"}))

    fetched_qr = api.client.apps.channels.qr.get(app_id="app", channel_id="channel", format="png")

    assert fetched_qr == b"png"
    assert api.sent_methods_and_urls == [f"GET {QR_URL}?format=png"]


def test_raises_not_found_when_the_app_has_no_channel_link_template() -> None:
    api = StubApi(
        httpx.Response(
            404, json={"code": "not_found", "message": "The app has no channel link template."}
        )
    )

    with pytest.raises(HotCodePushError) as raised:
        api.client.apps.channels.qr.get(app_id="app", channel_id="channel")

    assert (raised.value.code, raised.value.status) == ("not_found", 404)
