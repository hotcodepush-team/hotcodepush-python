import httpx
import pytest

from hotcodepush import HotCodePushError
from tests.stub_api import StubApi


def test_returns_when_the_api_answers_its_plain_text_ok() -> None:
    api = StubApi(httpx.Response(200, text="ok"))

    api.client.health.get()

    assert api.last_request.method == "GET"
    assert str(api.last_request.url) == "https://api.hotcodepush.com/health"


def test_raises_unexpected_response_with_the_status_when_the_api_answers_unavailable() -> None:
    api = StubApi(httpx.Response(503, text="unavailable"))

    with pytest.raises(HotCodePushError) as raised:
        api.client.health.get()

    assert (raised.value.code, raised.value.status) == ("unexpected_response", 503)
