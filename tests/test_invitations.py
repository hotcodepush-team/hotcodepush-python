import httpx
import pytest

from hotcodepush import Count, HotCodePushError, Invitation, Member
from tests.openapi_document import resolve_response_example
from tests.stub_api import StubApi, resolve_sent_json

INVITATION_ROW = resolve_response_example("POST", "/v1/organizations/{organizationId}/invitations")
INVITATIONS_URL = "https://api.hotcodepush.com/v1/invitations"
MEMBER_ROW = resolve_response_example("POST", "/v1/invitations/{invitationId}/accept")


def test_posts_the_token_to_accept_the_invitation() -> None:
    api = StubApi(httpx.Response(201, json=MEMBER_ROW))

    accepted_member = api.client.invitations.accept(invitation_id="invitation", token="token")

    assert accepted_member == Member.model_validate(MEMBER_ROW)
    assert api.sent_methods_and_urls == [f"POST {INVITATIONS_URL}/invitation/accept"]
    assert resolve_sent_json(api.last_request) == {"token": "token"}


def test_does_not_retry_the_acceptance_when_the_api_is_unavailable() -> None:
    api = StubApi(httpx.Response(503))

    with pytest.raises(HotCodePushError):
        api.client.invitations.accept(invitation_id="invitation", token="token")

    assert len(api.requests) == 1


def test_counts_the_callers_pending_invitations() -> None:
    api = StubApi(httpx.Response(200, json={"count": 3}))

    fetched_count = api.client.invitations.count()

    assert fetched_count == Count(count=3)
    assert api.sent_methods_and_urls == [f"GET {INVITATIONS_URL}/count"]


def test_lists_the_callers_pending_invitations() -> None:
    api = StubApi(httpx.Response(200, json=[INVITATION_ROW]))

    fetched_invitations = api.client.invitations.list()

    assert fetched_invitations == [Invitation.model_validate(INVITATION_ROW)]
    assert api.sent_methods_and_urls == [f"GET {INVITATIONS_URL}"]


def test_lists_the_callers_invitations_with_their_organizations_when_the_relation_is_set() -> None:
    api = StubApi(httpx.Response(200, json=resolve_response_example("GET", "/v1/invitations")))

    fetched_invitations = api.client.invitations.list(relations=["organization"])

    [fetched_invitation] = fetched_invitations
    assert fetched_invitation.organization is not None
    assert api.sent_methods_and_urls == [f"GET {INVITATIONS_URL}?relations=organization"]
