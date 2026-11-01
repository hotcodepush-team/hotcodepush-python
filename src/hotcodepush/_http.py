from __future__ import annotations

import re
from collections.abc import Callable, Mapping, Sequence
from datetime import UTC, date, datetime
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
# The API counts its rate limits in sixty-second windows.
MAX_RETRY_AFTER_SECONDS = 60.0
PATH_PARAMETER_PATTERN = re.compile(r"\{(\w+)\}")
RETRY_AFTER_STATUSES = frozenset({429, 503})
# Enough for the single-upload limit at about 100 kB a second.
UPLOAD_TIMEOUT_SECONDS = 600.0

HttpMethod = Literal["DELETE", "GET", "PATCH", "POST", "PUT"]
JsonBody = Mapping[str, object]
Query = Mapping[str, bool | date | datetime | int | str | Sequence[str] | NotGiven]
UploadBody = bytes | BinaryIO
"""The body of an upload: bytes, which a failed attempt sends again, or a file object, read once
and never retried."""

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
        if self._is_httpx_client_owned:
            self._httpx_client.close()

    def fetch_bytes(self, method: HttpMethod, path: str, *, query: Query | None = None) -> bytes:
        return self._fetch_response(method, path, query=query).content

    def fetch_creating_post(
        self,
        path: str,
        *,
        body: JsonBody,
        idempotency_key: str | NotGiven,
        response_type: type[T],
    ) -> T:
        resolved_idempotency_key = (
            str(uuid4()) if isinstance(idempotency_key, NotGiven) else idempotency_key
        )
        # The API answers a repeated key with the first result, so a retry is safe.
        return self.fetch_json(
            "POST",
            path,
            body=body,
            headers={"Idempotency-Key": resolved_idempotency_key},
            is_retryable=True,
            response_type=response_type,
        )

    def fetch_json(
        self,
        method: HttpMethod,
        path: str,
        *,
        body: JsonBody | None = None,
        headers: Mapping[str, str] | None = None,
        is_retryable: bool | None = None,
        query: Query | None = None,
        response_type: type[T],
    ) -> T:
        response = self._fetch_response(
            method, path, body=body, headers=headers, is_retryable=is_retryable, query=query
        )
        return TypeAdapter(response_type).validate_json(response.content)

    def fetch_status(
        self,
        method: HttpMethod,
        path: str,
        *,
        body: JsonBody | None = None,
        is_retryable: bool | None = None,
        query: Query | None = None,
    ) -> None:
        self._fetch_response(method, path, body=body, is_retryable=is_retryable, query=query)

    def fetch_upload(
        self,
        path: str,
        *,
        body: UploadBody,
        content_length: int | None,
        content_type: str,
        response_type: type[T],
    ) -> T:
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
    return {
        name: resolve_json_value(value)
        for name, value in body.items()
        if not isinstance(value, NotGiven)
    }


def resolve_json_value(value: object) -> object:
    if isinstance(value, BaseModel):
        # No nested field of the API takes `null`.
        return value.model_dump(by_alias=True, exclude_none=True, mode="json")
    if isinstance(value, datetime):
        return resolve_utc_timestamp(value)
    if isinstance(value, list):
        return [resolve_json_value(item) for item in value]
    return value


def resolve_path(template: str, **parameters: int | str) -> str:
    def resolve_parameter(match: re.Match[str]) -> str:
        name = match.group(1)
        if name not in parameters:
            raise ValueError(f"The path parameter {name} of {template} is missing.")
        return quote(str(parameters[name]), safe="")

    return PATH_PARAMETER_PATTERN.sub(resolve_parameter, template)


def resolve_query_params(query: Query) -> tuple[tuple[str, str], ...]:
    params: list[tuple[str, str]] = []
    for name, value in query.items():
        if isinstance(value, NotGiven) or value == "" or value == []:
            continue
        if isinstance(value, list):
            # Other lists repeat their parameter, since their values may hold a comma.
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
    # The API accepts only the `Z` offset.
    return value.astimezone(UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def send_with_retry(send: Callable[[], httpx.Response]) -> httpx.Response:
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
