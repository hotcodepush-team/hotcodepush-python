"""The one place that sends a request: the headers, the timeout, the retry, JSON in and out."""

from __future__ import annotations

import re
from collections.abc import Callable, Mapping, Sequence
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from time import sleep
from typing import BinaryIO, Literal, TypeVar
from urllib.parse import quote
from uuid import uuid4

import httpx
from pydantic import BaseModel, TypeAdapter

from ._types import NotGiven
from ._version import __version__
from .exceptions import resolve_hot_code_push_error

COMMA_LIST_QUERY_NAMES = frozenset({"ids", "relations"})
DEFAULT_BASE_URL = "https://api.hotcodepush.com"
DEFAULT_CLIENT = f"python/{__version__}"
IDEMPOTENT_METHODS = frozenset({"DELETE", "GET", "PUT"})
INITIAL_RETRY_DELAY_SECONDS = 0.5
JSON_TIMEOUT_SECONDS = 60.0
MAX_ATTEMPTS = 3
MAX_RETRY_AFTER_SECONDS = 60.0
"""The longest wait a `Retry-After` is followed for: the API's rate limits count in sixty-second
windows."""
PATH_PARAMETER_PATTERN = re.compile(r"\{(\w+)\}")
RETRY_AFTER_STATUSES = frozenset({429, 503})
UPLOAD_TIMEOUT_SECONDS = 600.0
"""Ten minutes per attempt: the single-upload limit at about a hundred kilobytes a second."""

HttpMethod = Literal["DELETE", "GET", "PATCH", "POST", "PUT"]
JsonBody = Mapping[str, object]
Query = Mapping[str, bool | datetime | int | str | Sequence[str] | NotGiven]
UploadBody = bytes | BinaryIO
"""Bytes, read again when a retry needs them, or a file object, read once and never retried."""

T = TypeVar("T")


class HttpClient:
    def __init__(
        self,
        *,
        base_url: str,
        client: str,
        http_client: httpx.Client | None,
        timeout: float | None,
        token: str | None,
        user_agent: str | None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._headers = resolve_headers(client=client, token=token, user_agent=user_agent)
        self._httpx_client = http_client or httpx.Client()
        self._is_httpx_client_owned = http_client is None
        self._json_timeout_seconds = JSON_TIMEOUT_SECONDS if timeout is None else timeout

    def close(self) -> None:
        """Closes the connection pool, unless the caller passed its own `http_client`."""
        if self._is_httpx_client_owned:
            self._httpx_client.close()

    def fetch_creating_post(
        self,
        path: str,
        response_type: type[T],
        *,
        body: JsonBody,
        idempotency_key: str | NotGiven,
    ) -> T:
        """A creating `POST`, sent with an `Idempotency-Key`: the caller's, or one generated
        for this call and kept across its retries, which the API answers with the first result.
        """
        resolved_idempotency_key = (
            str(uuid4()) if isinstance(idempotency_key, NotGiven) else idempotency_key
        )
        return self.fetch_json(
            "POST",
            path,
            response_type,
            body=body,
            headers={"Idempotency-Key": resolved_idempotency_key},
            is_retryable=True,
        )

    def fetch_json(
        self,
        method: HttpMethod,
        path: str,
        response_type: type[T],
        *,
        body: JsonBody | None = None,
        headers: Mapping[str, str] | None = None,
        is_retryable: bool | None = None,
        query: Query | None = None,
    ) -> T:
        """A request answered with JSON, validated into `response_type`.

        `is_retryable` defaults to true for `DELETE`, `GET` and `PUT`, false for `PATCH` and
        `POST`; a `POST` sets it where the API makes a repeat safe, through a stored idempotency
        key or a transition that answers a repeat unchanged.
        """
        response = self._fetch_response(
            method, path, body=body, headers=headers, is_retryable=is_retryable, query=query
        )
        return TypeAdapter(response_type).validate_json(response.content)

    def fetch_status(self, method: HttpMethod, path: str, *, query: Query | None = None) -> None:
        """A request whose status is the whole answer: the body, such as `/health`'s
        plain-text `ok`, is discarded.
        """
        self._fetch_response(method, path, query=query)

    def fetch_upload(
        self,
        path: str,
        response_type: type[T],
        *,
        body: UploadBody,
        content_length: int | None,
        content_type: str,
    ) -> T:
        """A binary `PUT`, streamed as it is read; a file object is read once, so only bytes
        are retried.
        """
        request = self._httpx_client.build_request(
            "PUT",
            self._base_url + path,
            content=body,
            headers={
                **self._headers,
                "Content-Length": str(resolve_content_length(body, content_length)),
                "Content-Type": content_type,
            },
            timeout=UPLOAD_TIMEOUT_SECONDS,
        )
        response = self._send(request, is_retryable=isinstance(body, bytes))
        return TypeAdapter(response_type).validate_json(response.content)

    def _fetch_response(
        self,
        method: HttpMethod,
        path: str,
        *,
        body: JsonBody | None = None,
        headers: Mapping[str, str] | None = None,
        is_retryable: bool | None = None,
        query: Query | None = None,
    ) -> httpx.Response:
        request = self._httpx_client.build_request(
            method,
            self._base_url + path,
            headers={**self._headers, **(headers or {})},
            json=None if body is None else resolve_json_body(body),
            params=resolve_query_params(query or {}),
            timeout=self._json_timeout_seconds,
        )
        return self._send(
            request,
            is_retryable=method in IDEMPOTENT_METHODS if is_retryable is None else is_retryable,
        )

    def _send(self, request: httpx.Request, *, is_retryable: bool) -> httpx.Response:
        def send() -> httpx.Response:
            return self._httpx_client.send(request)

        response = send_with_retry(send) if is_retryable else send()
        if not response.is_success:
            raise resolve_hot_code_push_error(response.status_code, response.text)
        return response


def is_retryable_status(status: int) -> bool:
    return status in (408, 429) or status >= 500


def resolve_content_length(body: UploadBody, content_length: int | None) -> int:
    if isinstance(body, bytes):
        return len(body)
    if content_length is None:
        raise ValueError("A file object body needs its content_length.")
    return content_length


def resolve_headers(*, client: str, token: str | None, user_agent: str | None) -> dict[str, str]:
    headers = {"Accept": "application/json", "X-HotCodePush-Client": client}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if user_agent:
        headers["User-Agent"] = user_agent
    return headers


def resolve_json_body(body: JsonBody) -> dict[str, object]:
    """The body without its `NOT_GIVEN` values, models by their API names and timestamps in UTC."""
    return {
        name: resolve_json_value(value)
        for name, value in body.items()
        if not isinstance(value, NotGiven)
    }


def resolve_json_value(value: object) -> object:
    if isinstance(value, BaseModel):
        return value.model_dump(by_alias=True, mode="json")
    if isinstance(value, datetime):
        return resolve_utc_timestamp(value)
    if isinstance(value, list):
        return [resolve_json_value(item) for item in value]
    return value


def resolve_path(template: str, **parameters: int | str) -> str:
    """Fills a path template of the OpenAPI snapshot, `/v1/apps/{appId}`, with its encoded
    parameters.
    """

    def resolve_parameter(match: re.Match[str]) -> str:
        name = match.group(1)
        if name not in parameters:
            raise ValueError(f"The path parameter {name} of {template} is missing.")
        return quote(str(parameters[name]), safe="")

    return PATH_PARAMETER_PATTERN.sub(resolve_parameter, template)


def resolve_query_params(query: Query) -> tuple[tuple[str, str], ...]:
    """The query as name and value pairs: `NOT_GIVEN`, empty strings and empty lists are left
    out; `ids` and `relations` are the API's comma lists, and every other list repeats its
    parameter, `?binary=…&binary=…`, since its values may hold a comma.
    """
    params: list[tuple[str, str]] = []
    for name, value in query.items():
        if isinstance(value, NotGiven) or value == "" or value == []:
            continue
        if isinstance(value, list):
            values = [",".join(value)] if name in COMMA_LIST_QUERY_NAMES else value
            params.extend((name, item) for item in values)
        elif isinstance(value, bool):
            params.append((name, "true" if value else "false"))
        elif isinstance(value, datetime):
            params.append((name, resolve_utc_timestamp(value)))
        else:
            params.append((name, str(value)))
    return tuple(params)


def resolve_retry_after_seconds(response: httpx.Response) -> float | None:
    """The wait a 429 or a 503 asks for in `Retry-After`, delay seconds or an HTTP date, capped
    at `MAX_RETRY_AFTER_SECONDS`; None for any other status, a missing header or one that does
    not parse.
    """
    retry_after = response.headers.get("Retry-After", "").strip()
    if response.status_code not in RETRY_AFTER_STATUSES or not retry_after:
        return None
    if retry_after.isdigit():
        retry_after_seconds = float(retry_after)
    else:
        try:
            retry_at = parsedate_to_datetime(retry_after)
        except ValueError:
            return None
        retry_after_seconds = (retry_at - datetime.now(UTC)).total_seconds()
    return min(max(retry_after_seconds, 0.0), MAX_RETRY_AFTER_SECONDS)


def resolve_utc_timestamp(value: datetime) -> str:
    """ISO 8601 in UTC with a `Z`, the only offset the API accepts."""
    return value.astimezone(UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def send_with_retry(send: Callable[[], httpx.Response]) -> httpx.Response:
    """Sends up to `MAX_ATTEMPTS` times on a transport error, 408, 429 and 5xx, backing off
    exponentially from `INITIAL_RETRY_DELAY_SECONDS`, or waiting a 429's or a 503's
    `Retry-After`; the last attempt's response or error is the call's.
    """
    attempt = 1
    while True:
        is_last_attempt = attempt == MAX_ATTEMPTS
        retry_after_seconds = None
        try:
            response = send()
        except httpx.TransportError:
            if is_last_attempt:
                raise
        else:
            if is_last_attempt or not is_retryable_status(response.status_code):
                return response
            response.close()
            retry_after_seconds = resolve_retry_after_seconds(response)
        if retry_after_seconds is None:
            retry_after_seconds = INITIAL_RETRY_DELAY_SECONDS * 2 ** (attempt - 1)
        sleep(retry_after_seconds)
        attempt += 1
