import httpx
import pytest

from hotcodepush import Checkout, HotCodePushError
from tests.stub_api import StubApi

CHECKOUT_ROW = {"url": "https://polar.sh/checkout/checkout"}


def test_posts_without_an_idempotency_key_to_create_the_checkout() -> None:
    api = StubApi(httpx.Response(201, json=CHECKOUT_ROW))

    created_checkout = api.client.organizations.checkouts.create(organization_id="organization")

    assert created_checkout == Checkout.model_validate(CHECKOUT_ROW)
    assert api.sent_methods_and_urls == [
        "POST https://api.hotcodepush.com/v1/organizations/organization/checkouts"
    ]
    assert api.last_request.content == b""
    assert "Idempotency-Key" not in api.last_request.headers


def test_does_not_retry_the_checkout_when_the_api_is_unavailable() -> None:
    api = StubApi(httpx.Response(503))

    with pytest.raises(HotCodePushError):
        api.client.organizations.checkouts.create(organization_id="organization")

    assert len(api.requests) == 1
