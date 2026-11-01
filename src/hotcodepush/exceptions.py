from __future__ import annotations

import json
from typing import Literal

ErrorCode = Literal[
    "account_banned",
    "app_name_taken",
    "apps_limit_reached",
    "auth_flow_failed",
    "binary_conflict",
    "bundle_in_use",
    "bundle_not_ready",
    "bundle_too_large",
    "channel_name_taken",
    "channel_protected",
    "channels_per_app_limit_reached",
    "client_update_required",
    "country_not_allowed",
    "default_channel",
    "dns_lookup_failed",
    "files_per_bundle_limit_reached",
    "forbidden",
    "hash_mismatch",
    "idempotency_key_reused",
    "internal",
    "invitation_invalid",
    "invitations_per_day_limit_reached",
    "ip_not_allowed",
    "maintenance",
    "members_limit_reached",
    "not_found",
    "notification_mandatory",
    "origin_untrusted",
    "password_already_set",
    "plan_required",
    "rate_limited",
    "release_revoked",
    "releases_per_day_limit_reached",
    "signature_invalid",
    "signature_required",
    "sole_owner",
    "sso_required",
    "storage_limit_reached",
    "tokens_limit_reached",
    "two_factor_required",
    "unauthenticated",
    "unexpected_response",
    "upload_incomplete",
    "validation",
    "webhook_name_taken",
]
"""A known code: one of the API's error catalog, or `unexpected_response` for a body without its shape."""


class HotCodePushError(Exception):
    """Raised when the API answers with a status outside 2xx.

    `code`, `message` and `details` come verbatim from the API's error body, so `code` is a `str`:
    a code newer than this client passes through, and `ErrorCode` lists the known ones. A response
    without that shape, such as a page from a proxy in front of the API, raises
    `unexpected_response` with the status and without the body.
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
            code=code,
            details=body.get("details"),
            message=message,
            status=status,
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
