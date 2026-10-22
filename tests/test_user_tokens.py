import httpx

from tests.stub_api import StubApi


def test_deletes_the_tokens_of_the_caller_named_by_the_ids_when_the_user_id_is_me() -> None:
    api = StubApi(httpx.Response(204))

    api.client.users.tokens.delete_many(ids=["first", "second"], user_id="me")

    assert api.sent_methods_and_urls == [
        "DELETE https://api.hotcodepush.com/v1/users/me/tokens?ids=first%2Csecond"
    ]
