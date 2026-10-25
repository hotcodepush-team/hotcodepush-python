"""The error raised for an API answer outside 2xx."""

from __future__ import annotations

import json


class HotCodePushError(Exception):
    """Raised when the API answers with a status outside 2xx.

    `code`, `message` and `details` are the API's, verbatim, from its one error shape;
    a response outside that shape, such as a page of the platform in front of the API,
    is `unexpected_response` with the status, its body left out.
    """

    def __init__(self, *, code: str, details: object, message: str, status: int) -> None:
        super().__init__(message)
        self.code = code
        self.details = details
        self.message = message
        self.status = status


def resolve_hot_code_push_error(status: int, text: str) -> HotCodePushError:
    body = resolve_json_object(text)
    code, message = body.get("code"), body.get("message")
    if isinstance(code, str) and isinstance(message, str):
        return HotCodePushError(
            code=code, details=body.get("details"), message=message, status=status
        )
    return HotCodePushError(
        code="unexpected_response",
        details=None,
        message=f"Request failed with status {status}.",
        status=status,
    )


def resolve_json_object(text: str) -> dict[str, object]:
    """The JSON object the text holds; empty when it holds none, such as an HTML page."""
    try:
        body: object = json.loads(text)
    except ValueError:
        return {}
    return body if isinstance(body, dict) else {}
