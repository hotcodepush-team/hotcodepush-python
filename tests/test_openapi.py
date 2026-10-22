"""The contract test: every resource method against the OpenAPI snapshot."""

import inspect
import io
from collections.abc import Callable
from functools import reduce
from typing import Any

import httpx
import pytest
from pydantic import BaseModel

from hotcodepush import (
    BinaryCondition,
    BundleSignature,
    HotCodePush,
    ManifestFile,
    ReleaseProgression,
    UploadedPart,
)
from hotcodepush.resources._base import BaseResource
from tests.openapi_document import (
    resolve_branches,
    resolve_documented_operation_names,
    resolve_operation,
    resolve_path_template,
    resolve_schema_example,
)
from tests.stub_api import StubApi, resolve_sent_json

APP_ID = "7c0f3a52-1d8e-4b6a-9f21-5e3c8a0d4b17"
BUNDLE_ID = "2a9e6c14-8b3f-4d70-a5e2-91c7f0b3d864"
CHANNEL_ID = "e41b7d09-3c6a-4f85-b2d1-6a8f0c9e3b52"
FILE = ManifestFile(path="index.html", sha256="a" * 64, size_bytes=5)
ORGANIZATION_ID = "c6e0b3a8-4d1f-4a92-b7e5-8f3d2c0a6b19"
RELEASE_ID = "0f7d4c2b-9a6e-4e18-83b5-d1c9a7f2e604"
SESSION_ONLY_NOTE = "An API token answers `E_FORBIDDEN`; sign in with a session."
SHA256 = "a" * 64
UPLOAD_ID = "upload"

CALLS: dict[str, Callable[[HotCodePush], object]] = {
    "apps.bundles.complete": lambda hot_code_push: hot_code_push.apps.bundles.complete(
        app_id=APP_ID, bundle_id=BUNDLE_ID
    ),
    "apps.bundles.count": lambda hot_code_push: hot_code_push.apps.bundles.count(
        app_id=APP_ID,
        fingerprint=f"fp1:{SHA256}",
        is_in_use=True,
        platform="ios",
        query="12",
        source="upload",
        status="ready",
        version="1.0.0",
    ),
    "apps.bundles.create": lambda hot_code_push: hot_code_push.apps.bundles.create(
        app_id=APP_ID,
        files=[FILE],
        fingerprint=f"fp1:{SHA256}",
        git_message="Fix the login",
        git_ref="main",
        git_remote="https://github.com/acme/demo.git",
        git_sha="b" * 40,
        idempotency_key="key",
        is_git_dirty=False,
        platforms=["android"],
        signature=BundleSignature(key_id="key", value="signature"),
        version="1.0.0",
    ),
    "apps.bundles.delete": lambda hot_code_push: hot_code_push.apps.bundles.delete(
        app_id=APP_ID, bundle_id=BUNDLE_ID
    ),
    "apps.bundles.get": lambda hot_code_push: hot_code_push.apps.bundles.get(
        app_id=APP_ID, bundle_id=BUNDLE_ID
    ),
    "apps.bundles.list": lambda hot_code_push: hot_code_push.apps.bundles.list(
        app_id=APP_ID,
        fingerprint=f"fp1:{SHA256}",
        is_in_use=True,
        limit=10,
        offset=10,
        platform="ios",
        query="12",
        source="upload",
        status="ready",
        version="1.0.0",
    ),
    "apps.bundles.pack.upload": lambda hot_code_push: hot_code_push.apps.bundles.pack.upload(
        app_id=APP_ID, body=io.BytesIO(b"pack"), bundle_id=BUNDLE_ID, content_length=4
    ),
    "apps.bundles.pack.uploads.complete": lambda hot_code_push: (
        hot_code_push.apps.bundles.pack.uploads.complete(
            app_id=APP_ID,
            bundle_id=BUNDLE_ID,
            parts=[UploadedPart(etag="etag", part_number=1)],
            upload_id=UPLOAD_ID,
        )
    ),
    "apps.bundles.pack.uploads.create": lambda hot_code_push: (
        hot_code_push.apps.bundles.pack.uploads.create(app_id=APP_ID, bundle_id=BUNDLE_ID)
    ),
    "apps.bundles.pack.uploads.delete": lambda hot_code_push: (
        hot_code_push.apps.bundles.pack.uploads.delete(
            app_id=APP_ID, bundle_id=BUNDLE_ID, upload_id=UPLOAD_ID
        )
    ),
    "apps.bundles.pack.uploads.parts.upload": lambda hot_code_push: (
        hot_code_push.apps.bundles.pack.uploads.parts.upload(
            app_id=APP_ID, body=b"part", bundle_id=BUNDLE_ID, part_number=1, upload_id=UPLOAD_ID
        )
    ),
    "apps.channels.count": lambda hot_code_push: hot_code_push.apps.channels.count(
        app_id=APP_ID, query="stag"
    ),
    "apps.channels.create": lambda hot_code_push: hot_code_push.apps.channels.create(
        app_id=APP_ID,
        expires_at=None,
        failure_action="pause",
        failure_minimum_update_count=20,
        failure_threshold_percent=10,
        idempotency_key="key",
        is_discoverable=True,
        is_protected=True,
        name="staging",
    ),
    "apps.channels.delete": lambda hot_code_push: hot_code_push.apps.channels.delete(
        app_id=APP_ID, channel_id=CHANNEL_ID
    ),
    "apps.channels.delete_many": lambda hot_code_push: hot_code_push.apps.channels.delete_many(
        app_id=APP_ID, ids=[CHANNEL_ID]
    ),
    "apps.channels.get": lambda hot_code_push: hot_code_push.apps.channels.get(
        app_id=APP_ID, channel_id=CHANNEL_ID
    ),
    "apps.channels.list": lambda hot_code_push: hot_code_push.apps.channels.list(
        app_id=APP_ID, limit=10, offset=10, query="stag"
    ),
    "apps.channels.pause": lambda hot_code_push: hot_code_push.apps.channels.pause(
        app_id=APP_ID, channel_id=CHANNEL_ID
    ),
    "apps.channels.releases.count": lambda hot_code_push: (
        hot_code_push.apps.channels.releases.count(app_id=APP_ID, channel_id=CHANNEL_ID, number=1)
    ),
    "apps.channels.releases.create": lambda hot_code_push: (
        hot_code_push.apps.channels.releases.create(
            app_id=APP_ID,
            bundle_id=BUNDLE_ID,
            channel_id=CHANNEL_ID,
            conditions=[BinaryCondition(range=">=2.0.0")],
            failure_action="pause",
            failure_minimum_update_count=20,
            failure_threshold_percent=10,
            from_channel_id=CHANNEL_ID,
            idempotency_key="key",
            is_mandatory=True,
            notes="Fixes the login.",
            progression=ReleaseProgression(
                percentages=[25, 50], step_minimum_seconds=3600, step_minimum_update_count=100
            ),
            rollout_percentage=10,
        )
    ),
    "apps.channels.releases.list": lambda hot_code_push: hot_code_push.apps.channels.releases.list(
        app_id=APP_ID,
        channel_id=CHANNEL_ID,
        limit=10,
        number=1,
        offset=10,
        relations=["bundle", "channel", "releaseCounters"],
    ),
    "apps.channels.releases.revoke": lambda hot_code_push: (
        hot_code_push.apps.channels.releases.revoke(
            app_id=APP_ID, channel_id=CHANNEL_ID, from_number=3, release_ids=[RELEASE_ID]
        )
    ),
    "apps.channels.resume": lambda hot_code_push: hot_code_push.apps.channels.resume(
        app_id=APP_ID, channel_id=CHANNEL_ID
    ),
    "apps.channels.update": lambda hot_code_push: hot_code_push.apps.channels.update(
        app_id=APP_ID,
        channel_id=CHANNEL_ID,
        expires_at=None,
        failure_action=None,
        failure_minimum_update_count=None,
        failure_threshold_percent=None,
        is_discoverable=False,
        is_protected=False,
        name="beta",
    ),
    "apps.delete": lambda hot_code_push: hot_code_push.apps.delete(app_id=APP_ID),
    "apps.get": lambda hot_code_push: hot_code_push.apps.get(app_id=APP_ID),
    "apps.transfer": lambda hot_code_push: hot_code_push.apps.transfer(
        app_id=APP_ID, organization_id=ORGANIZATION_ID
    ),
    "apps.update": lambda hot_code_push: hot_code_push.apps.update(
        app_id=APP_ID,
        channel_link_template="demo://channels/{channelId}",
        default_channel_id=CHANNEL_ID,
        framework="expo",
        name="Demo",
    ),
    "organizations.apps.count": lambda hot_code_push: hot_code_push.organizations.apps.count(
        organization_id=ORGANIZATION_ID, query="demo"
    ),
    "organizations.apps.create": lambda hot_code_push: hot_code_push.organizations.apps.create(
        framework="capacitor", idempotency_key="key", name="Demo", organization_id=ORGANIZATION_ID
    ),
    "organizations.apps.list": lambda hot_code_push: hot_code_push.organizations.apps.list(
        limit=10, offset=10, organization_id=ORGANIZATION_ID, query="demo"
    ),
    "organizations.count": lambda hot_code_push: hot_code_push.organizations.count(),
    "organizations.create": lambda hot_code_push: hot_code_push.organizations.create(
        idempotency_key="key", name="Acme"
    ),
    "organizations.delete": lambda hot_code_push: hot_code_push.organizations.delete(
        organization_id=ORGANIZATION_ID
    ),
    "organizations.get": lambda hot_code_push: hot_code_push.organizations.get(
        organization_id=ORGANIZATION_ID
    ),
    "organizations.list": lambda hot_code_push: hot_code_push.organizations.list(
        limit=10, offset=10
    ),
    "organizations.update": lambda hot_code_push: hot_code_push.organizations.update(
        country_allowlist=["DE"],
        ip_allowlist=["203.0.113.0/24"],
        is_two_factor_required=True,
        name="Acme",
        organization_id=ORGANIZATION_ID,
        spending_cap_cents=50_000,
    ),
}
"""One call per resource method with every option it can send, so a path, method, query
parameter, body field, content type or response field the document lacks fails here."""

UNIMPLEMENTED_OPERATIONS = frozenset(
    {
        "GET /v1/apps/{appId}/binaries",
        "POST /v1/apps/{appId}/binaries",
        "GET /v1/apps/{appId}/binaries/count",
        "GET /v1/apps/{appId}/binaries/{binaryId}",
        "GET /v1/apps/{appId}/bundles/{bundleId}/deltas",
        "GET /v1/apps/{appId}/bundles/{bundleId}/deltas/count",
        "GET /v1/apps/{appId}/bundles/{bundleId}/files",
        "GET /v1/apps/{appId}/bundles/{bundleId}/files/count",
        "GET /v1/apps/{appId}/channels/{channelId}/audience",
        "GET /v1/apps/{appId}/channels/{channelId}/qr",
        "POST /v1/apps/{appId}/channels/{channelId}/rollbacks",
        "DELETE /v1/apps/{appId}/devices",
        "GET /v1/apps/{appId}/devices",
        "GET /v1/apps/{appId}/devices/count",
        "DELETE /v1/apps/{appId}/devices/{deviceId}",
        "GET /v1/apps/{appId}/devices/{deviceId}",
        "GET /v1/apps/{appId}/devices/{deviceId}/events",
        "GET /v1/apps/{appId}/devices/{deviceId}/events/count",
        "PUT /v1/apps/{appId}/files/{sha256}",
        "POST /v1/apps/{appId}/files/{sha256}/uploads",
        "DELETE /v1/apps/{appId}/files/{sha256}/uploads/{uploadId}",
        "POST /v1/apps/{appId}/files/{sha256}/uploads/{uploadId}/complete",
        "PUT /v1/apps/{appId}/files/{sha256}/uploads/{uploadId}/parts/{partNumber}",
        "GET /v1/apps/{appId}/releases",
        "GET /v1/apps/{appId}/releases/count",
        "GET /v1/apps/{appId}/releases/{releaseId}",
        "PATCH /v1/apps/{appId}/releases/{releaseId}",
        "GET /v1/apps/{appId}/releases/{releaseId}/audience",
        "POST /v1/apps/{appId}/releases/{releaseId}/pause",
        "POST /v1/apps/{appId}/releases/{releaseId}/resume",
        "POST /v1/apps/{appId}/releases/{releaseId}/revoke",
        "GET /v1/apps/{appId}/signing-keys",
        "POST /v1/apps/{appId}/signing-keys",
        "GET /v1/apps/{appId}/signing-keys/count",
        "DELETE /v1/apps/{appId}/signing-keys/{signingKeyId}",
        "GET /v1/apps/{appId}/statistics/fleet",
        "GET /v1/apps/{appId}/statistics/updates",
        "GET /v1/apps/{appId}/statistics/usage",
        "GET /v1/invitations",
        "GET /v1/invitations/count",
        "POST /v1/invitations/{invitationId}/accept",
        "GET /v1/notification-preferences",
        "PATCH /v1/notification-preferences",
        "GET /v1/notifications",
        "PATCH /v1/notifications",
        "GET /v1/notifications/count",
        "PATCH /v1/notifications/{notificationId}",
        "GET /v1/organizations/{organizationId}/audit-logs",
        "GET /v1/organizations/{organizationId}/audit-logs/count",
        "POST /v1/organizations/{organizationId}/checkouts",
        "POST /v1/organizations/{organizationId}/customer-portal-sessions",
        "DELETE /v1/organizations/{organizationId}/invitations",
        "GET /v1/organizations/{organizationId}/invitations",
        "POST /v1/organizations/{organizationId}/invitations",
        "GET /v1/organizations/{organizationId}/invitations/count",
        "DELETE /v1/organizations/{organizationId}/invitations/{invitationId}",
        "GET /v1/organizations/{organizationId}/limits",
        "DELETE /v1/organizations/{organizationId}/members",
        "GET /v1/organizations/{organizationId}/members",
        "GET /v1/organizations/{organizationId}/members/count",
        "DELETE /v1/organizations/{organizationId}/members/{memberId}",
        "GET /v1/organizations/{organizationId}/members/{memberId}",
        "PATCH /v1/organizations/{organizationId}/members/{memberId}",
        "DELETE /v1/organizations/{organizationId}/sso-provider",
        "GET /v1/organizations/{organizationId}/sso-provider",
        "PUT /v1/organizations/{organizationId}/sso-provider",
        "POST /v1/organizations/{organizationId}/sso-provider/verifications",
        "POST /v1/organizations/{organizationId}/subscription/cancel",
        "POST /v1/organizations/{organizationId}/subscription/uncancel",
        "GET /v1/organizations/{organizationId}/usage",
        "GET /v1/organizations/{organizationId}/usage/apps",
        "GET /v1/organizations/{organizationId}/usage/apps/count",
        "GET /v1/organizations/{organizationId}/webhooks",
        "POST /v1/organizations/{organizationId}/webhooks",
        "GET /v1/organizations/{organizationId}/webhooks/count",
        "DELETE /v1/organizations/{organizationId}/webhooks/{webhookId}",
        "GET /v1/organizations/{organizationId}/webhooks/{webhookId}",
        "PATCH /v1/organizations/{organizationId}/webhooks/{webhookId}",
        "GET /v1/organizations/{organizationId}/webhooks/{webhookId}/deliveries",
        "GET /v1/organizations/{organizationId}/webhooks/{webhookId}/deliveries/count",
        "POST /v1/organizations/{organizationId}/webhooks/{webhookId}/deliveries/{deliveryId}/redeliver",
        "POST /v1/organizations/{organizationId}/webhooks/{webhookId}/test",
        "DELETE /v1/users/{userId}",
        "GET /v1/users/{userId}",
        "POST /v1/users/{userId}/password",
        "DELETE /v1/users/{userId}/sessions",
        "DELETE /v1/users/{userId}/tokens",
    }
)
"""The operations of the snapshot no resource method calls yet, ordered by path; an operation
leaves this list with the method that calls it."""

UNDOCUMENTED_RESOURCES = frozenset({"health"})
"""`/health` is outside the document by the path rule."""


class SnapshotApi(StubApi):
    """Answers every request with the example of its operation's documented 2xx response."""

    def respond(self, request: httpx.Request) -> httpx.Response:
        template = resolve_path_template(request.url.path)
        if template is None:
            return httpx.Response(404)
        responses = resolve_operation(request.method, template)["responses"]
        status, response = next(
            (status, response) for status, response in responses.items() if status.startswith("2")
        )
        content = response.get("content", {})
        if "application/json" in content:
            return httpx.Response(
                int(status), json=resolve_schema_example(content["application/json"]["schema"])
            )
        return httpx.Response(int(status))


def test_holds_a_call_for_every_resource_method() -> None:
    with HotCodePush() as hot_code_push:
        resource_method_names = [
            method_name
            for name, resource in vars(hot_code_push).items()
            if isinstance(resource, BaseResource) and name not in UNDOCUMENTED_RESOURCES
            for method_name in resolve_resource_method_names(resource, name)
        ]

    assert sorted(CALLS) == sorted(resource_method_names)


def test_calls_every_operation_the_snapshot_documents_but_the_unimplemented_ones() -> None:
    api = SnapshotApi()

    for call in CALLS.values():
        call(api.client)

    called_operation_names = {
        f"{request.method} {resolve_path_template(request.url.path)}" for request in api.requests
    }
    missing_operation_names = resolve_documented_operation_names() - called_operation_names
    assert missing_operation_names == UNIMPLEMENTED_OPERATIONS, (
        f"Called by no method and not listed as unimplemented: "
        f"{sorted(missing_operation_names - UNIMPLEMENTED_OPERATIONS)}; "
        f"called, yet still listed as unimplemented: "
        f"{sorted(UNIMPLEMENTED_OPERATIONS - missing_operation_names)}"
    )


@pytest.mark.parametrize("name", sorted(CALLS))
def test_documents_the_path_method_query_idempotency_key_body_and_content_type_a_call_sends(
    name: str,
) -> None:
    api = SnapshotApi()

    CALLS[name](api.client)

    request = api.last_request
    template = resolve_path_template(request.url.path)
    assert template is not None, f"{request.url.path} is not in openapi.json"
    operation = resolve_operation(request.method, template)
    parameters = operation.get("parameters", [])
    documented_query_names = {
        parameter["name"] for parameter in parameters if parameter.get("in") == "query"
    }
    has_documented_idempotency_key = any(
        parameter.get("in") == "header" and parameter["name"] == "Idempotency-Key"
        for parameter in parameters
    )
    documented_content = operation.get("requestBody", {}).get("content", {})
    assert set(request.url.params) <= documented_query_names
    assert ("Idempotency-Key" in request.headers) == has_documented_idempotency_key
    assert bool(request.content) == bool(documented_content)
    if request.content:
        content_type = request.headers["Content-Type"]
        assert content_type in documented_content
        if content_type == "application/json":
            body_schema = documented_content[content_type]["schema"]
            assert (
                resolve_undocumented_fields(resolve_sent_json(request), body_schema, "body") == []
            )


@pytest.mark.parametrize("name", sorted(CALLS))
def test_declares_every_field_of_the_response_a_call_reads(name: str) -> None:
    api = SnapshotApi()

    response_value = CALLS[name](api.client)

    assert resolve_undeclared_fields(response_value, name) == []


@pytest.mark.parametrize("name", sorted(CALLS))
def test_notes_the_refusal_of_an_api_token_exactly_where_the_operation_is_session_only(
    name: str,
) -> None:
    api = SnapshotApi()

    CALLS[name](api.client)

    request = api.last_request
    operation = resolve_operation(request.method, resolve_path_template(request.url.path) or "")
    is_session_only = any(
        "sessionAuth" in requirement for requirement in operation.get("security", [])
    )
    method = reduce(getattr, name.split("."), api.client)
    assert (SESSION_ONLY_NOTE in (inspect.getdoc(method) or "")) == is_session_only


def resolve_resource_method_names(resource: BaseResource, path: str) -> list[str]:
    method_names = [
        f"{path}.{name}"
        for name, _ in inspect.getmembers(type(resource), inspect.isfunction)
        if not name.startswith("_")
    ]
    nested_method_names = [
        method_name
        for name, nested_resource in vars(resource).items()
        if isinstance(nested_resource, BaseResource)
        for method_name in resolve_resource_method_names(nested_resource, f"{path}.{name}")
    ]
    return method_names + nested_method_names


def resolve_undeclared_fields(value: object, path: str) -> list[str]:
    """The response fields a model keeps in `model_extra`: documented, yet not declared."""
    if isinstance(value, list):
        return [
            undeclared_field
            for index, item in enumerate(value)
            for undeclared_field in resolve_undeclared_fields(item, f"{path}[{index}]")
        ]
    if not isinstance(value, BaseModel):
        return []
    nested_undeclared_fields = [
        undeclared_field
        for name in type(value).model_fields
        for undeclared_field in resolve_undeclared_fields(getattr(value, name), f"{path}.{name}")
    ]
    return [f"{path}.{name}" for name in value.model_extra or {}] + nested_undeclared_fields


def resolve_undocumented_fields(value: object, schema: dict[str, Any], path: str) -> list[str]:
    """The fields of a sent body its schema lacks, nested objects and list items included."""
    if isinstance(value, list):
        item_schema = next(
            branch["items"] for branch in resolve_branches(schema) if "items" in branch
        )
        return [
            undocumented_field
            for index, item in enumerate(value)
            for undocumented_field in resolve_undocumented_fields(
                item, item_schema, f"{path}[{index}]"
            )
        ]
    if not isinstance(value, dict):
        return []
    properties = {
        name: property_schema
        for branch in resolve_branches(schema)
        for name, property_schema in branch.get("properties", {}).items()
    }
    return [
        undocumented_field
        for name, item in value.items()
        for undocumented_field in (
            resolve_undocumented_fields(item, properties[name], f"{path}.{name}")
            if name in properties
            else [f"{path}.{name}"]
        )
    ]
