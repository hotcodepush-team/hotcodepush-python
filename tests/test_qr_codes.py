import httpx
import pytest

from hotcodepush import HotCodePushError
from tests.stub_api import StubApi


def test_gets_the_qr_image_of_the_url_in_the_given_format_and_size() -> None:
    api = StubApi(httpx.Response(200, content=b"png", headers={"Content-Type": "image/png"}))

    fetched_qr_code = api.client.qr_codes.get(
        format="png", size=512, url="https://hotcodepush.com/docs"
    )

    assert fetched_qr_code == b"png"
    assert api.sent_methods_and_urls == [
        "GET https://api.hotcodepush.com/v1/qr-codes"
        "?format=png&size=512&url=https%3A%2F%2Fhotcodepush.com%2Fdocs"
    ]


def test_raises_validation_when_the_url_is_on_another_host() -> None:
    api = StubApi(
        httpx.Response(
            400,
            json={
                "code": "validation",
                "details": {"field": "url", "rule": "host_not_allowed"},
                "message": "The URL must be on hotcodepush.com.",
            },
        )
    )

    with pytest.raises(HotCodePushError) as raised:
        api.client.qr_codes.get(url="https://example.com")

    assert raised.value.code == "validation"
    assert raised.value.details == {"field": "url", "rule": "host_not_allowed"}
