from __future__ import annotations

import json


class HotCodePushError(Exception):
    """Raised when the API answers with a status outside 2xx.

    `code`, `message` and `details` come verbatim from the API's error body. A response without
    that shape, such as a page from a proxy in front of the API, raises `unexpected_response` with
    the status and without the body.
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
    try:
        body: object = json.loads(text)
    except ValueError:
        return {}
    return body if isinstance(body, dict) else {}
