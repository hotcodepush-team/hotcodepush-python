import httpx
import pytest

from hotcodepush import Count, HotCodePushError, SigningKey
from tests.openapi_document import resolve_response_example
from tests.stub_api import StubApi, resolve_sent_json

SIGNING_KEY_ROW = resolve_response_example("POST", "/v1/apps/{appId}/signing-keys")
SIGNING_KEYS_URL = "https://api.hotcodepush.com/v1/apps/app/signing-keys"


def test_counts_the_signing_keys_of_the_app() -> None:
    api = StubApi(httpx.Response(200, json={"count": 1}))

    fetched_count = api.client.apps.signing_keys.count(app_id="app")

    assert fetched_count == Count(count=1)
    assert api.sent_methods_and_urls == [f"GET {SIGNING_KEYS_URL}/count"]


def test_posts_the_public_key() -> None:
    api = StubApi(httpx.Response(201, json=SIGNING_KEY_ROW))

    created_signing_key = api.client.apps.signing_keys.create(
        app_id="app", public_key="rsa-v1_5-sha256:a2V5"
    )

    assert created_signing_key == SigningKey.model_validate(SIGNING_KEY_ROW)
    assert api.sent_methods_and_urls == [f"POST {SIGNING_KEYS_URL}"]
    assert resolve_sent_json(api.last_request) == {"publicKey": "rsa-v1_5-sha256:a2V5"}


def test_retries_the_registration_when_the_api_is_unavailable() -> None:
    api = StubApi(httpx.Response(503))

    with pytest.raises(HotCodePushError):
        api.client.apps.signing_keys.create(app_id="app", public_key="rsa-v1_5-sha256:a2V5")

    assert len(api.requests) == 3


def test_deletes_the_signing_key() -> None:
    api = StubApi(httpx.Response(204))

    api.client.apps.signing_keys.delete(app_id="app", signing_key_id="signing-key")

    assert api.sent_methods_and_urls == [f"DELETE {SIGNING_KEYS_URL}/signing-key"]


def test_lists_the_signing_keys_of_the_app() -> None:
    api = StubApi(httpx.Response(200, json=[SIGNING_KEY_ROW]))

    fetched_signing_keys = api.client.apps.signing_keys.list(app_id="app", limit=20)

    assert fetched_signing_keys == [SigningKey.model_validate(SIGNING_KEY_ROW)]
    assert api.sent_methods_and_urls == [f"GET {SIGNING_KEYS_URL}?limit=20"]
