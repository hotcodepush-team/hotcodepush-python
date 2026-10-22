import httpx

from hotcodepush import Count, Invitation
from tests.openapi_document import resolve_response_example
from tests.stub_api import StubApi, resolve_sent_json

INVITATION_ROW = resolve_response_example("POST", "/v1/organizations/{organizationId}/invitations")
INVITATIONS_URL = "https://api.hotcodepush.com/v1/organizations/organization/invitations"


def test_counts_the_pending_invitations_of_the_organization() -> None:
    api = StubApi(httpx.Response(200, json={"count": 3}))

    fetched_count = api.client.organizations.invitations.count(
        organization_id="organization", status="pending"
    )

    assert fetched_count == Count(count=3)
    assert api.sent_methods_and_urls == [f"GET {INVITATIONS_URL}/count?status=pending"]


def test_posts_the_invitation_with_its_idempotency_key() -> None:
    api = StubApi(httpx.Response(201, json=INVITATION_ROW))

    created_invitation = api.client.organizations.invitations.create(
        email="jane@example.com",
        idempotency_key="key",
        organization_id="organization",
        role="admin",
    )

    assert created_invitation == Invitation.model_validate(INVITATION_ROW)
    assert api.sent_methods_and_urls == [f"POST {INVITATIONS_URL}"]
    assert api.last_request.headers["Idempotency-Key"] == "key"
    assert resolve_sent_json(api.last_request) == {"email": "jane@example.com", "role": "admin"}


def test_deletes_the_invitation() -> None:
    api = StubApi(httpx.Response(204))

    api.client.organizations.invitations.delete(
        invitation_id="invitation", organization_id="organization"
    )

    assert api.sent_methods_and_urls == [f"DELETE {INVITATIONS_URL}/invitation"]


def test_deletes_the_invitations_named_by_the_ids() -> None:
    api = StubApi(httpx.Response(204))

    api.client.organizations.invitations.delete_many(
        ids=["first", "second"], organization_id="organization"
    )

    assert api.sent_methods_and_urls == [f"DELETE {INVITATIONS_URL}?ids=first%2Csecond"]


def test_lists_the_invitations_of_the_organization() -> None:
    api = StubApi(httpx.Response(200, json=[INVITATION_ROW]))

    fetched_invitations = api.client.organizations.invitations.list(
        limit=5, organization_id="organization"
    )

    assert fetched_invitations == [Invitation.model_validate(INVITATION_ROW)]
    assert api.sent_methods_and_urls == [f"GET {INVITATIONS_URL}?limit=5"]
