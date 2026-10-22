import httpx

from hotcodepush import Count, Member
from tests.openapi_document import resolve_response_example
from tests.stub_api import StubApi, resolve_sent_json

MEMBER_ROW = resolve_response_example(
    "PATCH", "/v1/organizations/{organizationId}/members/{memberId}"
)
MEMBER_ROW_WITH_RELATIONS = resolve_response_example(
    "GET", "/v1/organizations/{organizationId}/members/{memberId}"
)
MEMBERS_URL = "https://api.hotcodepush.com/v1/organizations/organization/members"


def test_counts_the_members_of_the_organization_under_the_filters() -> None:
    api = StubApi(httpx.Response(200, json={"count": 3}))

    fetched_count = api.client.organizations.members.count(
        organization_id="organization", role="admin"
    )

    assert fetched_count == Count(count=3)
    assert api.sent_methods_and_urls == [f"GET {MEMBERS_URL}/count?role=admin"]


def test_deletes_the_member() -> None:
    api = StubApi(httpx.Response(204))

    api.client.organizations.members.delete(member_id="member", organization_id="organization")

    assert api.sent_methods_and_urls == [f"DELETE {MEMBERS_URL}/member"]


def test_deletes_the_members_named_by_the_ids() -> None:
    api = StubApi(httpx.Response(204))

    api.client.organizations.members.delete_many(
        ids=["first", "second"], organization_id="organization"
    )

    assert api.sent_methods_and_urls == [f"DELETE {MEMBERS_URL}?ids=first%2Csecond"]


def test_gets_the_member() -> None:
    api = StubApi(httpx.Response(200, json=MEMBER_ROW))

    fetched_member = api.client.organizations.members.get(
        member_id="member", organization_id="organization"
    )

    assert fetched_member == Member.model_validate(MEMBER_ROW)
    assert api.sent_methods_and_urls == [f"GET {MEMBERS_URL}/member"]


def test_gets_the_member_with_its_user_and_accounts_when_the_relations_are_set() -> None:
    api = StubApi(httpx.Response(200, json=MEMBER_ROW_WITH_RELATIONS))

    fetched_member = api.client.organizations.members.get(
        member_id="member", organization_id="organization", relations=["user", "user.accounts"]
    )

    assert fetched_member.user is not None
    assert fetched_member.user.accounts is not None
    assert api.sent_methods_and_urls == [f"GET {MEMBERS_URL}/member?relations=user%2Cuser.accounts"]


def test_lists_the_members_with_their_users_when_the_user_relation_is_set() -> None:
    api = StubApi(httpx.Response(200, json=[MEMBER_ROW_WITH_RELATIONS]))

    fetched_members = api.client.organizations.members.list(
        limit=10, organization_id="organization", relations=["user"]
    )

    assert fetched_members == [Member.model_validate(MEMBER_ROW_WITH_RELATIONS)]
    assert api.sent_methods_and_urls == [f"GET {MEMBERS_URL}?limit=10&relations=user"]


def test_patches_the_role_of_the_member() -> None:
    api = StubApi(httpx.Response(200, json=MEMBER_ROW))

    updated_member = api.client.organizations.members.update(
        member_id="member", organization_id="organization", role="owner"
    )

    assert updated_member == Member.model_validate(MEMBER_ROW)
    assert api.sent_methods_and_urls == [f"PATCH {MEMBERS_URL}/member"]
    assert resolve_sent_json(api.last_request) == {"role": "owner"}
