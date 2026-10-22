import httpx

from hotcodepush import User
from tests.openapi_document import resolve_response_example
from tests.stub_api import StubApi, resolve_sent_json

USER_ROW = resolve_response_example("GET", "/v1/users/{userId}")
USERS_URL = "https://api.hotcodepush.com/v1/users"


def test_deletes_the_caller_with_the_password_when_the_user_id_is_me() -> None:
    api = StubApi(httpx.Response(204))

    api.client.users.delete(password="correct horse battery staple", user_id="me")

    assert api.sent_methods_and_urls == [f"DELETE {USERS_URL}/me"]
    assert resolve_sent_json(api.last_request) == {"password": "correct horse battery staple"}


def test_gets_the_caller_when_the_user_id_is_me() -> None:
    api = StubApi(httpx.Response(200, json=USER_ROW))

    fetched_user = api.client.users.get(user_id="me")

    assert fetched_user == User.model_validate(USER_ROW)
    assert api.sent_methods_and_urls == [f"GET {USERS_URL}/me"]


def test_gets_the_caller_with_their_members_and_organizations_when_the_relations_are_set() -> None:
    api = StubApi(httpx.Response(200, json=USER_ROW))

    fetched_user = api.client.users.get(relations=["members", "members.organization"], user_id="me")

    assert fetched_user.members is not None
    [fetched_member] = fetched_user.members
    assert fetched_member.organization is not None
    assert api.sent_methods_and_urls == [
        f"GET {USERS_URL}/me?relations=members%2Cmembers.organization"
    ]
