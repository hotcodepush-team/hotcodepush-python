import httpx
import pytest

from hotcodepush import HotCodePushError
from tests.stub_api import StubApi, resolve_sent_json

SUBSCRIPTION_URL = "https://api.hotcodepush.com/v1/organizations/organization/subscription"


def test_posts_the_reason_and_the_comment_to_cancel_the_subscription() -> None:
    api = StubApi(httpx.Response(204))

    api.client.organizations.subscription.cancel(
        comment="Too expensive for us.", organization_id="organization", reason="too_expensive"
    )

    assert api.sent_methods_and_urls == [f"POST {SUBSCRIPTION_URL}/cancel"]
    assert resolve_sent_json(api.last_request) == {
        "comment": "Too expensive for us.",
        "reason": "too_expensive",
    }


def test_retries_the_cancel_when_the_api_is_unavailable() -> None:
    api = StubApi(httpx.Response(503))

    with pytest.raises(HotCodePushError):
        api.client.organizations.subscription.cancel(organization_id="organization", reason="other")

    assert len(api.requests) == 3


def test_posts_to_uncancel_the_subscription() -> None:
    api = StubApi(httpx.Response(204))

    api.client.organizations.subscription.uncancel(organization_id="organization")

    assert api.sent_methods_and_urls == [f"POST {SUBSCRIPTION_URL}/uncancel"]
    assert api.last_request.content == b""


def test_retries_the_uncancel_when_the_api_is_unavailable() -> None:
    api = StubApi(httpx.Response(503))

    with pytest.raises(HotCodePushError):
        api.client.organizations.subscription.uncancel(organization_id="organization")

    assert len(api.requests) == 3
