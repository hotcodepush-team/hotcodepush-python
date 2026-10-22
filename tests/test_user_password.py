import httpx
import pytest

from hotcodepush import HotCodePushError
from tests.stub_api import StubApi, resolve_sent_json


def test_posts_the_first_password_of_the_caller_when_the_user_id_is_me() -> None:
    api = StubApi(httpx.Response(204))

    api.client.users.password.create(password="correct horse battery staple", user_id="me")

    assert api.sent_methods_and_urls == ["POST https://api.hotcodepush.com/v1/users/me/password"]
    assert resolve_sent_json(api.last_request) == {"password": "correct horse battery staple"}


def test_does_not_retry_the_password_when_the_api_is_unavailable() -> None:
    api = StubApi(httpx.Response(503))

    with pytest.raises(HotCodePushError):
        api.client.users.password.create(password="correct horse battery staple", user_id="me")

    assert len(api.requests) == 1
