import io
from datetime import UTC, datetime, timedelta, timezone
from email.utils import format_datetime

import httpx
import pytest

from hotcodepush import (
    NOT_GIVEN,
    HotCodePush,
    HotCodePushError,
    ManifestFile,
    OidcConfig,
    __version__,
)
from hotcodepush._http import (
    HttpMethod,
    resolve_path,
    resolve_query_params,
    send_with_retry,
)
from hotcodepush.models import Count
from tests.stub_api import StubApi, resolve_sent_json

UNREACHABLE_BASE_URL = "http://127.0.0.1:9"


def test_gives_each_json_attempt_sixty_seconds() -> None:
    api = StubApi()

    api.client.health.get()

    assert api.last_request.extensions["timeout"]["read"] == 60.0


def test_gives_each_json_attempt_the_given_timeout_when_a_timeout_is_set() -> None:
    api = StubApi()

    HotCodePush(http_client=api.http_client, timeout=5.0).health.get()

    assert api.last_request.extensions["timeout"]["read"] == 5.0


def test_requests_the_default_base_url_when_no_base_url_is_set() -> None:
    api = StubApi()

    api.client.health.get()

    assert str(api.last_request.url) == "https://api.hotcodepush.com/health"


def test_requests_the_given_base_url_when_a_base_url_is_set() -> None:
    api = StubApi()

    HotCodePush(base_url="http://localhost:8787/", http_client=api.http_client).health.get()

    assert str(api.last_request.url) == "http://localhost:8787/health"


def test_sends_the_token_as_a_bearer_when_a_token_is_set() -> None:
    api = StubApi()

    HotCodePush("token", http_client=api.http_client).health.get()

    assert api.last_request.headers["Authorization"] == "Bearer token"


def test_sends_the_token_of_the_environment_when_no_token_is_set(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("HOTCODEPUSH_TOKEN", "environment-token")
    api = StubApi()

    api.client.health.get()

    assert api.last_request.headers["Authorization"] == "Bearer environment-token"


def test_sends_no_authorization_when_no_token_is_set() -> None:
    api = StubApi()

    api.client.health.get()

    assert "Authorization" not in api.last_request.headers


def test_sends_python_and_the_package_version_as_the_client_when_no_client_is_set() -> None:
    api = StubApi()

    api.client.health.get()

    assert api.last_request.headers["X-HotCodePush-Client"] == f"python/{__version__}"


def test_sends_the_given_client_when_a_client_is_set() -> None:
    api = StubApi()

    HotCodePush(client="cli/1.2.3", http_client=api.http_client).health.get()

    assert api.last_request.headers["X-HotCodePush-Client"] == "cli/1.2.3"


def test_sends_the_given_user_agent_when_a_user_agent_is_set() -> None:
    api = StubApi()

    HotCodePush(http_client=api.http_client, user_agent="hotcodepush-cli/1.2.3").health.get()

    assert api.last_request.headers["User-Agent"] == "hotcodepush-cli/1.2.3"


def test_leaves_the_user_agent_to_httpx_when_no_user_agent_is_set() -> None:
    api = StubApi()

    api.client.health.get()

    assert api.last_request.headers["User-Agent"].startswith("python-httpx/")


def test_sends_the_body_as_json_without_its_not_given_values_when_a_body_is_set() -> None:
    api = StubApi(httpx.Response(200, json={"count": 1}))

    api.create_http_client().fetch_json(
        "POST", "/v1/apps/app/channels", Count, body={"name": "production", "notes": NOT_GIVEN}
    )

    assert api.last_request.headers["Content-Type"] == "application/json"
    assert resolve_sent_json(api.last_request) == {"name": "production"}


def test_sends_none_in_the_body_as_null() -> None:
    api = StubApi(httpx.Response(200, json={"count": 1}))

    api.create_http_client().fetch_json(
        "PATCH", "/v1/apps/app", Count, body={"channelLinkTemplate": None}
    )

    assert resolve_sent_json(api.last_request) == {"channelLinkTemplate": None}


def test_sends_a_model_in_the_body_by_its_api_names() -> None:
    api = StubApi(httpx.Response(200, json={"count": 1}))

    api.create_http_client().fetch_json(
        "POST",
        "/v1/apps/app/bundles",
        Count,
        body={"files": [ManifestFile(path="index.html", sha256="a" * 64, size_bytes=5)]},
    )

    assert resolve_sent_json(api.last_request) == {
        "files": [{"path": "index.html", "sha256": "a" * 64, "sizeBytes": 5}]
    }


def test_sends_a_model_in_the_body_without_its_none_fields() -> None:
    api = StubApi(httpx.Response(200, json={"count": 1}))

    api.create_http_client().fetch_json(
        "PUT",
        "/v1/organizations/organization/sso-provider",
        Count,
        body={"oidc": OidcConfig(client_id="client", client_secret="secret", issuer="issuer")},
    )

    assert resolve_sent_json(api.last_request) == {
        "oidc": {"clientId": "client", "clientSecret": "secret", "issuer": "issuer"}
    }


def test_sends_a_timestamp_in_the_body_in_utc_with_a_z() -> None:
    api = StubApi(httpx.Response(200, json={"count": 1}))

    api.create_http_client().fetch_json(
        "PATCH",
        "/v1/apps/app/channels/channel",
        Count,
        body={"expiresAt": datetime(2026, 10, 1, 14, tzinfo=timezone(timedelta(hours=2)))},
    )

    assert resolve_sent_json(api.last_request) == {"expiresAt": "2026-10-01T12:00:00.000Z"}


def test_sends_the_query_without_its_not_given_values_and_empty_lists() -> None:
    assert resolve_query_params(
        {"limit": 10, "name": NOT_GIVEN, "offset": 0, "query": "", "relations": []}
    ) == (("limit", "10"), ("offset", "0"))


def test_sends_the_relations_in_the_query_as_a_comma_list() -> None:
    assert resolve_query_params({"relations": ["bundle", "channel"]}) == (
        ("relations", "bundle,channel"),
    )


def test_sends_the_ids_in_the_query_as_a_comma_list() -> None:
    assert resolve_query_params({"ids": ["first", "second"]}) == (("ids", "first,second"),)


def test_repeats_the_parameter_of_any_other_list_in_the_query() -> None:
    assert resolve_query_params(
        {"attribute": ["tier=gold,silver"], "binary": [">=2.0.0", "<3.0.0"]}
    ) == (("attribute", "tier=gold,silver"), ("binary", ">=2.0.0"), ("binary", "<3.0.0"))


def test_sends_a_boolean_in_the_query_as_true_or_false() -> None:
    assert resolve_query_params({"isInUse": True, "isStored": False}) == (
        ("isInUse", "true"),
        ("isStored", "false"),
    )


def test_sends_a_timestamp_in_the_query_in_utc_with_a_z() -> None:
    assert resolve_query_params({"createdSince": datetime(2026, 10, 1, tzinfo=UTC)}) == (
        ("createdSince", "2026-10-01T00:00:00.000Z"),
    )


def test_returns_the_validated_body_when_the_response_has_one() -> None:
    api = StubApi(httpx.Response(200, json={"count": 3}))

    fetched_count = api.create_http_client().fetch_json("GET", "/v1/organizations/count", Count)

    assert fetched_count == Count(count=3)


def test_returns_the_body_whole_when_the_response_is_binary() -> None:
    api = StubApi(httpx.Response(200, content=b"\x89PNG", headers={"Content-Type": "image/png"}))

    fetched_bytes = api.create_http_client().fetch_bytes(
        "GET", "/v1/apps/app/channels/channel/qr", query={"format": "png"}
    )

    assert fetched_bytes == b"\x89PNG"
    assert str(api.last_request.url) == (
        "https://api.hotcodepush.com/v1/apps/app/channels/channel/qr?format=png"
    )


def test_raises_a_hot_code_push_error_when_the_response_is_not_ok() -> None:
    api = StubApi(
        httpx.Response(401, json={"code": "E_UNAUTHENTICATED", "message": "The token is invalid."})
    )

    with pytest.raises(HotCodePushError) as raised:
        api.create_http_client().fetch_json("GET", "/v1/users/me", Count)

    assert (raised.value.code, raised.value.status) == ("E_UNAUTHENTICATED", 401)


def test_raises_e_unexpected_response_when_a_rate_limit_in_front_of_the_api_answers_html() -> None:
    api = StubApi(httpx.Response(429, text="<html>Too Many Requests</html>"))

    with pytest.raises(HotCodePushError) as raised:
        api.create_http_client().fetch_json("POST", "/v1/invitations/invitation/accept", Count)

    assert (raised.value.code, raised.value.status) == ("E_UNEXPECTED_RESPONSE", 429)


@pytest.mark.parametrize("method", ["DELETE", "GET", "PUT"])
def test_retries_a_request_when_the_api_is_unavailable(method: HttpMethod) -> None:
    api = StubApi(httpx.Response(503))

    with pytest.raises(HotCodePushError):
        api.create_http_client().fetch_status(method, "/v1/apps/app")

    assert len(api.requests) == 3


@pytest.mark.parametrize("method", ["PATCH", "POST"])
def test_does_not_retry_a_request_when_the_api_is_unavailable(method: HttpMethod) -> None:
    api = StubApi(httpx.Response(503))

    with pytest.raises(HotCodePushError):
        api.create_http_client().fetch_status(method, "/v1/apps/app")

    assert len(api.requests) == 1


def test_retries_a_post_when_the_api_is_unavailable_and_the_call_is_retryable() -> None:
    api = StubApi(httpx.Response(503))

    with pytest.raises(HotCodePushError):
        api.create_http_client().fetch_json(
            "POST", "/v1/apps/app/channels/channel/pause", Count, is_retryable=True
        )

    assert len(api.requests) == 3


def test_sends_the_body_of_a_status_request_as_json_when_a_body_is_set() -> None:
    api = StubApi(httpx.Response(204))

    api.create_http_client().fetch_status("DELETE", "/v1/users/me", body={"password": "secret"})

    assert api.last_request.headers["Content-Type"] == "application/json"
    assert resolve_sent_json(api.last_request) == {"password": "secret"}


def test_retries_a_status_post_when_the_api_is_unavailable_and_the_call_is_retryable() -> None:
    api = StubApi(httpx.Response(503))

    with pytest.raises(HotCodePushError):
        api.create_http_client().fetch_status(
            "POST", "/v1/organizations/organization/subscription/uncancel", is_retryable=True
        )

    assert len(api.requests) == 3


def test_leaves_the_given_http_client_open_when_closed() -> None:
    api = StubApi()

    api.client.close()

    assert not api.http_client.is_closed


def test_closes_its_own_http_client_when_closed() -> None:
    with HotCodePush(base_url=UNREACHABLE_BASE_URL) as hot_code_push:
        pass

    with pytest.raises(RuntimeError, match="closed"):
        hot_code_push.health.get()


def test_sends_the_given_idempotency_key_when_one_is_set() -> None:
    api = StubApi(httpx.Response(201, json={"count": 1}))

    api.create_http_client().fetch_creating_post(
        "/v1/organizations", Count, body={"name": "Acme"}, idempotency_key="key"
    )

    assert api.last_request.method == "POST"
    assert api.last_request.headers["Idempotency-Key"] == "key"
    assert resolve_sent_json(api.last_request) == {"name": "Acme"}


def test_sends_one_generated_idempotency_key_on_every_attempt_when_none_is_set() -> None:
    api = StubApi(httpx.Response(503), httpx.Response(201, json={"count": 1}))

    api.create_http_client().fetch_creating_post(
        "/v1/organizations", Count, body={"name": "Acme"}, idempotency_key=NOT_GIVEN
    )

    first_key, second_key = (request.headers["Idempotency-Key"] for request in api.requests)
    assert len(first_key) == 36
    assert second_key == first_key


def test_puts_bytes_with_their_size_as_the_content_length() -> None:
    api = StubApi(httpx.Response(200, json={"count": 1}))

    api.create_http_client().fetch_upload(
        "/v1/apps/app/files/sha256",
        Count,
        body=b"gzip bytes",
        content_length=None,
        content_type="application/gzip",
    )

    assert api.last_request.method == "PUT"
    assert api.last_request.content == b"gzip bytes"
    assert api.last_request.headers["Content-Length"] == "10"
    assert api.last_request.headers["Content-Type"] == "application/gzip"


def test_streams_a_file_object_with_the_given_content_length() -> None:
    api = StubApi(httpx.Response(200, json={"count": 1}))

    api.create_http_client().fetch_upload(
        "/v1/apps/app/bundles/bundle/pack",
        Count,
        body=io.BytesIO(b"tar bytes"),
        content_length=9,
        content_type="application/x-tar",
    )

    assert api.last_request.content == b"tar bytes"
    assert api.last_request.headers["Content-Length"] == "9"
    assert "Transfer-Encoding" not in api.last_request.headers


def test_raises_when_a_file_object_comes_without_its_content_length() -> None:
    api = StubApi()

    with pytest.raises(ValueError, match="content_length"):
        api.create_http_client().fetch_upload(
            "/v1/apps/app/bundles/bundle/pack",
            Count,
            body=io.BytesIO(b"tar bytes"),
            content_length=None,
            content_type="application/x-tar",
        )


def test_gives_each_upload_attempt_ten_minutes() -> None:
    api = StubApi(httpx.Response(200, json={"count": 1}))

    api.create_http_client().fetch_upload(
        "/v1/apps/app/bundles/bundle/pack",
        Count,
        body=b"tar bytes",
        content_length=None,
        content_type="application/x-tar",
    )

    assert api.last_request.extensions["timeout"]["write"] == 600.0


def test_retries_bytes_when_the_status_is_retryable() -> None:
    api = StubApi(httpx.Response(502), httpx.Response(200, json={"count": 9}))

    uploaded_count = api.create_http_client().fetch_upload(
        "/v1/apps/app/bundles/bundle/pack",
        Count,
        body=b"tar bytes",
        content_length=None,
        content_type="application/x-tar",
    )

    assert uploaded_count == Count(count=9)
    assert len(api.requests) == 2


def test_does_not_retry_a_file_object_which_is_read_once() -> None:
    api = StubApi(httpx.Response(503))

    with pytest.raises(HotCodePushError) as raised:
        api.create_http_client().fetch_upload(
            "/v1/apps/app/bundles/bundle/pack",
            Count,
            body=io.BytesIO(b"tar bytes"),
            content_length=9,
            content_type="application/x-tar",
        )

    assert raised.value.status == 503
    assert len(api.requests) == 1


def test_fills_the_path_template_with_the_encoded_parameters() -> None:
    assert (
        resolve_path("/v1/apps/{appId}/channels/{channelId}", appId="app", channelId="a/b")
        == "/v1/apps/app/channels/a%2Fb"
    )


def test_fills_a_number_path_parameter_as_its_digits() -> None:
    assert (
        resolve_path(
            "/v1/apps/{appId}/files/{sha256}/uploads/{uploadId}/parts/{partNumber}",
            appId="app",
            partNumber=2,
            sha256="sha256",
            uploadId="upload",
        )
        == "/v1/apps/app/files/sha256/uploads/upload/parts/2"
    )


def test_raises_when_a_path_parameter_is_missing() -> None:
    with pytest.raises(
        ValueError, match=r"The path parameter appId of /v1/apps/\{appId\} is missing."
    ):
        resolve_path("/v1/apps/{appId}")


@pytest.mark.parametrize("status", [408, 429, 500, 503])
def test_retries_three_times_when_the_status_is_retryable(status: int) -> None:
    sent_statuses: list[int] = []

    response = send_with_retry(lambda: record_response(sent_statuses, httpx.Response(status)))

    assert response.status_code == status
    assert sent_statuses == [status, status, status]


def test_does_not_retry_when_the_status_is_not_retryable() -> None:
    sent_statuses: list[int] = []

    response = send_with_retry(lambda: record_response(sent_statuses, httpx.Response(404)))

    assert response.status_code == 404
    assert sent_statuses == [404]


def test_backs_off_exponentially_between_attempts(recorded_sleeps: list[float]) -> None:
    responses = iter([httpx.Response(503), httpx.Response(503), httpx.Response(200)])

    response = send_with_retry(lambda: next(responses))

    assert response.status_code == 200
    assert recorded_sleeps == [0.5, 1.0]


@pytest.mark.parametrize("status", [429, 503])
def test_waits_the_seconds_of_retry_after_when_the_status_carries_them(
    status: int, recorded_sleeps: list[float]
) -> None:
    responses = iter([httpx.Response(status, headers={"Retry-After": "5"}), httpx.Response(200)])

    send_with_retry(lambda: next(responses))

    assert recorded_sleeps == [5.0]


def test_waits_until_the_date_of_retry_after_when_a_429_carries_one(
    recorded_sleeps: list[float],
) -> None:
    retry_at = format_datetime(datetime.now(UTC) + timedelta(seconds=3), usegmt=True)
    responses = iter([httpx.Response(429, headers={"Retry-After": retry_at}), httpx.Response(200)])

    send_with_retry(lambda: next(responses))

    [waited_seconds] = recorded_sleeps
    assert 1.0 < waited_seconds <= 3.0


def test_waits_at_most_sixty_seconds_when_the_retry_after_of_a_429_asks_for_longer(
    recorded_sleeps: list[float],
) -> None:
    responses = iter([httpx.Response(429, headers={"Retry-After": "3600"}), httpx.Response(200)])

    send_with_retry(lambda: next(responses))

    assert recorded_sleeps == [60.0]


@pytest.mark.parametrize("headers", [{}, {"Retry-After": "soon"}])
def test_backs_off_exponentially_when_a_429_carries_no_retry_after_that_parses(
    headers: dict[str, str], recorded_sleeps: list[float]
) -> None:
    responses = iter([httpx.Response(429, headers=headers), httpx.Response(200)])

    send_with_retry(lambda: next(responses))

    assert recorded_sleeps == [0.5]


def test_raises_the_last_error_when_every_attempt_raises(recorded_sleeps: list[float]) -> None:
    attempt_count = 0

    def raise_timeout() -> httpx.Response:
        nonlocal attempt_count
        attempt_count += 1
        raise httpx.ReadTimeout("The read timed out.")

    with pytest.raises(httpx.ReadTimeout):
        send_with_retry(raise_timeout)

    assert attempt_count == 3
    assert recorded_sleeps == [0.5, 1.0]


def record_response(sent_statuses: list[int], response: httpx.Response) -> httpx.Response:
    sent_statuses.append(response.status_code)
    return response
