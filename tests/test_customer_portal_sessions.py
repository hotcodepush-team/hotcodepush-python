import httpx
import pytest

from hotcodepush import CustomerPortalSession, HotCodePushError
from tests.stub_api import StubApi

CUSTOMER_PORTAL_SESSION_ROW = {"url": "https://polar.sh/portal/session"}


def test_posts_without_an_idempotency_key_to_create_the_customer_portal_session() -> None:
    api = StubApi(httpx.Response(201, json=CUSTOMER_PORTAL_SESSION_ROW))

    created_session = api.client.organizations.customer_portal_sessions.create(
        organization_id="organization"
    )

    assert created_session == CustomerPortalSession.model_validate(CUSTOMER_PORTAL_SESSION_ROW)
    assert api.sent_methods_and_urls == [
        "POST https://api.hotcodepush.com/v1/organizations/organization/customer-portal-sessions"
    ]
    assert api.last_request.content == b""
    assert "Idempotency-Key" not in api.last_request.headers


def test_does_not_retry_the_customer_portal_session_when_the_api_is_unavailable() -> None:
    api = StubApi(httpx.Response(503))

    with pytest.raises(HotCodePushError):
        api.client.organizations.customer_portal_sessions.create(organization_id="organization")

    assert len(api.requests) == 1
