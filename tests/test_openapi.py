import inspect
import io
from collections.abc import Callable
from datetime import UTC, date, datetime
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
    OidcConfig,
    ReleaseProgression,
    SamlConfig,
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
BINARY_ID = "3f6a9c2e-7b14-4d58-9e03-b2c8d6f1a475"
BUNDLE_ID = "2a9e6c14-8b3f-4d70-a5e2-91c7f0b3d864"
CHANNEL_ID = "e41b7d09-3c6a-4f85-b2d1-6a8f0c9e3b52"
CREATED_SINCE = datetime(2026, 1, 1, tzinfo=UTC)
CREATED_UNTIL = datetime(2026, 2, 1, tzinfo=UTC)
DELIVERY_ID = "8f2c6a41-5d9e-4b73-a1c8-0e7b3d5f9a26"
DEVICE_ID = "6b1e9d37-2f5c-4a80-9c46-d8e3a1f7b259"
FILE = ManifestFile(path="index.html", sha256="a" * 64, size_bytes=5)
INVITATION_ID = "9d3c5e81-6f2a-4b07-8c14-3e7a1f9b0d26"
MEMBER_ID = "5b8a2f47-0e9c-4d31-a6b8-2c4f7e1d9a03"
NOTIFICATION_ID = "7e2a5c19-4b8d-4f36-a0c7-1d9e3b6f8a52"
ORGANIZATION_ID = "c6e0b3a8-4d1f-4a92-b7e5-8f3d2c0a6b19"
PASSWORD = "correct horse battery staple"
RELEASE_ID = "0f7d4c2b-9a6e-4e18-83b5-d1c9a7f2e604"
SESSION_ID = "4e7b2d90-8c3a-4f61-b5d2-9a1c6e8f3b47"
SESSION_ONLY_NOTE = "An API token answers `forbidden`; sign in with a session."
SHA256 = "a" * 64
SIGNING_KEY_ID = "1c4f8a6d-3e92-4b57-a0d8-5f2b7c9e1a34"
TOKEN_ID = "8a3f1c6e-2d94-4b70-9e15-c7b4a2d8f063"
UPLOAD_ID = "upload"
USER_ID = "2d5c8f1a-7b36-4e09-a4c2-6f1e9b3d7a58"
WEBHOOK_ID = "3b9e1d74-6a2f-4c58-8d03-f5a7c2e9b416"

# Each call sends every option its method takes, so anything the snapshot lacks fails a test.
CALLS: dict[str, Callable[[HotCodePush], object]] = {
    "apps.binaries.count": lambda hot_code_push: hot_code_push.apps.binaries.count(
        app_id=APP_ID, fingerprint=f"fp1:{SHA256}", platform="ios"
    ),
    "apps.binaries.create": lambda hot_code_push: hot_code_push.apps.binaries.create(
        app_id=APP_ID,
        build="42",
        files=[FILE],
        fingerprint=f"fp1:{SHA256}",
        force=True,
        idempotency_key="key",
        platform="android",
        version="1.0.0",
    ),
    "apps.binaries.get": lambda hot_code_push: hot_code_push.apps.binaries.get(
        app_id=APP_ID, binary_id=BINARY_ID
    ),
    "apps.binaries.list": lambda hot_code_push: hot_code_push.apps.binaries.list(
        app_id=APP_ID, fingerprint=f"fp1:{SHA256}", limit=10, offset=10, platform="ios"
    ),
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
    "apps.bundles.deltas.count": lambda hot_code_push: hot_code_push.apps.bundles.deltas.count(
        app_id=APP_ID, bundle_id=BUNDLE_ID
    ),
    "apps.bundles.deltas.list": lambda hot_code_push: hot_code_push.apps.bundles.deltas.list(
        app_id=APP_ID, bundle_id=BUNDLE_ID, limit=10, offset=10, relations=["baseBundle"]
    ),
    "apps.bundles.files.count": lambda hot_code_push: hot_code_push.apps.bundles.files.count(
        app_id=APP_ID, bundle_id=BUNDLE_ID, is_stored=False
    ),
    "apps.bundles.files.list": lambda hot_code_push: hot_code_push.apps.bundles.files.list(
        app_id=APP_ID, bundle_id=BUNDLE_ID, is_stored=False, limit=10, offset=10
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
    "apps.channels.audience.get": lambda hot_code_push: hot_code_push.apps.channels.audience.get(
        app_id=APP_ID,
        attribute=["tier=gold"],
        binary=[">=2.0.0"],
        channel_id=CHANNEL_ID,
        device=[DEVICE_ID],
        fingerprint=[f"fp1:{SHA256}"],
        os=[">=17"],
        rollout_percentage=10,
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
    "apps.channels.qr.get": lambda hot_code_push: hot_code_push.apps.channels.qr.get(
        app_id=APP_ID, channel_id=CHANNEL_ID, format="png"
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
    "apps.channels.rollbacks.create": lambda hot_code_push: (
        hot_code_push.apps.channels.rollbacks.create(
            app_id=APP_ID,
            channel_id=CHANNEL_ID,
            idempotency_key="key",
            is_mandatory=False,
            to_release_id=RELEASE_ID,
        )
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
    "apps.devices.count": lambda hot_code_push: hot_code_push.apps.devices.count(
        app_id=APP_ID,
        attribute="tier=gold",
        binary_build="42",
        binary_version="1.0.0",
        channel_id=CHANNEL_ID,
        fingerprint=f"fp1:{SHA256}",
        last_seen_since=datetime(2026, 1, 1, tzinfo=UTC),
        last_seen_until=datetime(2026, 2, 1, tzinfo=UTC),
        platform="ios",
        sdk_version="1.0.0",
    ),
    "apps.devices.delete": lambda hot_code_push: hot_code_push.apps.devices.delete(
        app_id=APP_ID, device_id=DEVICE_ID
    ),
    "apps.devices.delete_many": lambda hot_code_push: hot_code_push.apps.devices.delete_many(
        app_id=APP_ID, ids=[DEVICE_ID]
    ),
    "apps.devices.events.count": lambda hot_code_push: hot_code_push.apps.devices.events.count(
        app_id=APP_ID, device_id=DEVICE_ID, release_id=RELEASE_ID
    ),
    "apps.devices.events.list": lambda hot_code_push: hot_code_push.apps.devices.events.list(
        app_id=APP_ID, device_id=DEVICE_ID, limit=10, offset=10, release_id=RELEASE_ID
    ),
    "apps.devices.get": lambda hot_code_push: hot_code_push.apps.devices.get(
        app_id=APP_ID, device_id=DEVICE_ID, relations=["channel", "currentRelease"]
    ),
    "apps.devices.list": lambda hot_code_push: hot_code_push.apps.devices.list(
        app_id=APP_ID,
        attribute="tier=gold",
        binary_build="42",
        binary_version="1.0.0",
        channel_id=CHANNEL_ID,
        fingerprint=f"fp1:{SHA256}",
        last_seen_since=datetime(2026, 1, 1, tzinfo=UTC),
        last_seen_until=datetime(2026, 2, 1, tzinfo=UTC),
        limit=10,
        offset=10,
        platform="ios",
        relations=["channel", "currentRelease"],
        sdk_version="1.0.0",
    ),
    "apps.files.upload": lambda hot_code_push: hot_code_push.apps.files.upload(
        app_id=APP_ID, body=io.BytesIO(b"gzip"), content_length=4, sha256=SHA256
    ),
    "apps.files.uploads.complete": lambda hot_code_push: hot_code_push.apps.files.uploads.complete(
        app_id=APP_ID,
        parts=[UploadedPart(etag="etag", part_number=1)],
        sha256=SHA256,
        upload_id=UPLOAD_ID,
    ),
    "apps.files.uploads.create": lambda hot_code_push: hot_code_push.apps.files.uploads.create(
        app_id=APP_ID, sha256=SHA256
    ),
    "apps.files.uploads.delete": lambda hot_code_push: hot_code_push.apps.files.uploads.delete(
        app_id=APP_ID, sha256=SHA256, upload_id=UPLOAD_ID
    ),
    "apps.files.uploads.parts.upload": lambda hot_code_push: (
        hot_code_push.apps.files.uploads.parts.upload(
            app_id=APP_ID, body=b"part", part_number=1, sha256=SHA256, upload_id=UPLOAD_ID
        )
    ),
    "apps.get": lambda hot_code_push: hot_code_push.apps.get(app_id=APP_ID),
    "apps.releases.audience.get": lambda hot_code_push: hot_code_push.apps.releases.audience.get(
        app_id=APP_ID, release_id=RELEASE_ID
    ),
    "apps.releases.count": lambda hot_code_push: hot_code_push.apps.releases.count(
        app_id=APP_ID,
        bundle_id=BUNDLE_ID,
        channel_id=CHANNEL_ID,
        git_commit="main",
        status="active",
    ),
    "apps.releases.get": lambda hot_code_push: hot_code_push.apps.releases.get(
        app_id=APP_ID, relations=["bundle", "channel", "releaseCounters"], release_id=RELEASE_ID
    ),
    "apps.releases.list": lambda hot_code_push: hot_code_push.apps.releases.list(
        app_id=APP_ID,
        bundle_id=BUNDLE_ID,
        channel_id=CHANNEL_ID,
        git_commit="main",
        limit=10,
        offset=10,
        relations=["bundle", "channel", "releaseCounters"],
        status="active",
    ),
    "apps.releases.pause": lambda hot_code_push: hot_code_push.apps.releases.pause(
        app_id=APP_ID, release_id=RELEASE_ID
    ),
    "apps.releases.resume": lambda hot_code_push: hot_code_push.apps.releases.resume(
        app_id=APP_ID, release_id=RELEASE_ID
    ),
    "apps.releases.revoke": lambda hot_code_push: hot_code_push.apps.releases.revoke(
        app_id=APP_ID, release_id=RELEASE_ID
    ),
    "apps.releases.update": lambda hot_code_push: hot_code_push.apps.releases.update(
        app_id=APP_ID,
        failure_action="pause",
        failure_minimum_update_count=20,
        failure_threshold_percent=10,
        is_mandatory=True,
        notes="Fixes the login.",
        progression=ReleaseProgression(
            percentages=[75, 100], step_minimum_seconds=3600, step_minimum_update_count=100
        ),
        release_id=RELEASE_ID,
        rollout_percentage=50,
    ),
    "apps.signing_keys.count": lambda hot_code_push: hot_code_push.apps.signing_keys.count(
        app_id=APP_ID
    ),
    "apps.signing_keys.create": lambda hot_code_push: hot_code_push.apps.signing_keys.create(
        app_id=APP_ID, public_key="rsa-v1_5-sha256:a2V5"
    ),
    "apps.signing_keys.delete": lambda hot_code_push: hot_code_push.apps.signing_keys.delete(
        app_id=APP_ID, signing_key_id=SIGNING_KEY_ID
    ),
    "apps.signing_keys.list": lambda hot_code_push: hot_code_push.apps.signing_keys.list(
        app_id=APP_ID, limit=10, offset=10
    ),
    "apps.statistics.fleet.get": lambda hot_code_push: hot_code_push.apps.statistics.fleet.get(
        app_id=APP_ID, channel_id=CHANNEL_ID
    ),
    "apps.statistics.updates.get": lambda hot_code_push: hot_code_push.apps.statistics.updates.get(
        app_id=APP_ID,
        channel_id=CHANNEL_ID,
        period_since=date(2026, 9, 1),
        period_until=date(2026, 9, 30),
        release_id=RELEASE_ID,
    ),
    "apps.statistics.usage.get": lambda hot_code_push: hot_code_push.apps.statistics.usage.get(
        app_id=APP_ID, period_since=date(2026, 9, 1), period_until=date(2026, 9, 30)
    ),
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
    "invitations.accept": lambda hot_code_push: hot_code_push.invitations.accept(
        invitation_id=INVITATION_ID, token="token"
    ),
    "invitations.count": lambda hot_code_push: hot_code_push.invitations.count(),
    "invitations.list": lambda hot_code_push: hot_code_push.invitations.list(
        limit=10, offset=10, relations=["organization"]
    ),
    "notification_preferences.list": lambda hot_code_push: (
        hot_code_push.notification_preferences.list(organization_id=ORGANIZATION_ID)
    ),
    "notification_preferences.update": lambda hot_code_push: (
        hot_code_push.notification_preferences.update(
            category="product_alerts",
            is_enabled=False,
            medium="email",
            organization_id=ORGANIZATION_ID,
        )
    ),
    "notifications.count": lambda hot_code_push: hot_code_push.notifications.count(is_read=False),
    "notifications.list": lambda hot_code_push: hot_code_push.notifications.list(
        is_read=False, limit=10, offset=10, relations=["app", "channel", "memberUser", "release"]
    ),
    "notifications.update": lambda hot_code_push: hot_code_push.notifications.update(
        is_read=True, notification_id=NOTIFICATION_ID
    ),
    "notifications.update_many": lambda hot_code_push: hot_code_push.notifications.update_many(
        is_read=True
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
    "organizations.audit_logs.count": lambda hot_code_push: (
        hot_code_push.organizations.audit_logs.count(
            actor_type="user",
            app_id=APP_ID,
            created_since=CREATED_SINCE,
            created_until=CREATED_UNTIL,
            organization_id=ORGANIZATION_ID,
            type="channel.*",
            user_id=USER_ID,
        )
    ),
    "organizations.audit_logs.download_csv": lambda hot_code_push: (
        hot_code_push.organizations.audit_logs.download_csv(
            actor_type="user",
            app_id=APP_ID,
            created_since=CREATED_SINCE,
            created_until=CREATED_UNTIL,
            organization_id=ORGANIZATION_ID,
            type="channel.*",
            user_id=USER_ID,
        )
    ),
    "organizations.audit_logs.list": lambda hot_code_push: (
        hot_code_push.organizations.audit_logs.list(
            actor_type="user",
            app_id=APP_ID,
            created_since=CREATED_SINCE,
            created_until=CREATED_UNTIL,
            limit=10,
            offset=10,
            organization_id=ORGANIZATION_ID,
            relations=["app", "user"],
            type="channel.*",
            user_id=USER_ID,
        )
    ),
    "organizations.checkouts.create": lambda hot_code_push: (
        hot_code_push.organizations.checkouts.create(organization_id=ORGANIZATION_ID)
    ),
    "organizations.count": lambda hot_code_push: hot_code_push.organizations.count(),
    "organizations.create": lambda hot_code_push: hot_code_push.organizations.create(
        idempotency_key="key", name="Acme"
    ),
    "organizations.customer_portal_sessions.create": lambda hot_code_push: (
        hot_code_push.organizations.customer_portal_sessions.create(organization_id=ORGANIZATION_ID)
    ),
    "organizations.delete": lambda hot_code_push: hot_code_push.organizations.delete(
        organization_id=ORGANIZATION_ID
    ),
    "organizations.get": lambda hot_code_push: hot_code_push.organizations.get(
        organization_id=ORGANIZATION_ID
    ),
    "organizations.invitations.count": lambda hot_code_push: (
        hot_code_push.organizations.invitations.count(
            organization_id=ORGANIZATION_ID, query="jane", role="member", status="pending"
        )
    ),
    "organizations.invitations.create": lambda hot_code_push: (
        hot_code_push.organizations.invitations.create(
            email="jane@example.com",
            idempotency_key="key",
            organization_id=ORGANIZATION_ID,
            role="member",
        )
    ),
    "organizations.invitations.delete": lambda hot_code_push: (
        hot_code_push.organizations.invitations.delete(
            invitation_id=INVITATION_ID, organization_id=ORGANIZATION_ID
        )
    ),
    "organizations.invitations.delete_many": lambda hot_code_push: (
        hot_code_push.organizations.invitations.delete_many(
            ids=[INVITATION_ID], organization_id=ORGANIZATION_ID
        )
    ),
    "organizations.invitations.list": lambda hot_code_push: (
        hot_code_push.organizations.invitations.list(
            limit=10,
            offset=10,
            organization_id=ORGANIZATION_ID,
            query="jane",
            role="member",
            status="pending",
        )
    ),
    "organizations.limits.get": lambda hot_code_push: hot_code_push.organizations.limits.get(
        organization_id=ORGANIZATION_ID
    ),
    "organizations.list": lambda hot_code_push: hot_code_push.organizations.list(
        limit=10, offset=10
    ),
    "organizations.members.count": lambda hot_code_push: hot_code_push.organizations.members.count(
        organization_id=ORGANIZATION_ID, query="jane", role="admin", user_id=USER_ID
    ),
    "organizations.members.delete": lambda hot_code_push: (
        hot_code_push.organizations.members.delete(
            member_id=MEMBER_ID, organization_id=ORGANIZATION_ID
        )
    ),
    "organizations.members.delete_many": lambda hot_code_push: (
        hot_code_push.organizations.members.delete_many(
            ids=[MEMBER_ID], organization_id=ORGANIZATION_ID
        )
    ),
    "organizations.members.get": lambda hot_code_push: hot_code_push.organizations.members.get(
        member_id=MEMBER_ID, organization_id=ORGANIZATION_ID, relations=["user", "user.accounts"]
    ),
    "organizations.members.list": lambda hot_code_push: hot_code_push.organizations.members.list(
        limit=10,
        offset=10,
        organization_id=ORGANIZATION_ID,
        query="jane",
        relations=["user", "user.accounts"],
        role="admin",
        user_id=USER_ID,
    ),
    "organizations.members.update": lambda hot_code_push: (
        hot_code_push.organizations.members.update(
            member_id=MEMBER_ID, organization_id=ORGANIZATION_ID, role="admin"
        )
    ),
    "organizations.sso_provider.delete": lambda hot_code_push: (
        hot_code_push.organizations.sso_provider.delete(organization_id=ORGANIZATION_ID)
    ),
    "organizations.sso_provider.get": lambda hot_code_push: (
        hot_code_push.organizations.sso_provider.get(organization_id=ORGANIZATION_ID)
    ),
    "organizations.sso_provider.put": lambda hot_code_push: (
        hot_code_push.organizations.sso_provider.put(
            domain="example.com",
            oidc=OidcConfig(
                client_id="client",
                client_secret="secret",
                discovery_endpoint="https://idp.example.com/.well-known/openid-configuration",
                issuer="https://idp.example.com",
                scopes=["openid"],
            ),
            organization_id=ORGANIZATION_ID,
            saml=SamlConfig(
                cert="certificate",
                entity_id="https://idp.example.com/saml",
                entry_point="https://idp.example.com/saml/sso",
                issuer="https://idp.example.com",
                metadata="<EntityDescriptor/>",
            ),
        )
    ),
    "organizations.sso_provider.verifications.create": lambda hot_code_push: (
        hot_code_push.organizations.sso_provider.verifications.create(
            organization_id=ORGANIZATION_ID
        )
    ),
    "organizations.subscription.cancel": lambda hot_code_push: (
        hot_code_push.organizations.subscription.cancel(
            comment="We moved to a monthly release train.",
            organization_id=ORGANIZATION_ID,
            reason="not_enough_value",
        )
    ),
    "organizations.subscription.uncancel": lambda hot_code_push: (
        hot_code_push.organizations.subscription.uncancel(organization_id=ORGANIZATION_ID)
    ),
    "organizations.update": lambda hot_code_push: hot_code_push.organizations.update(
        country_allowlist=["DE"],
        ip_allowlist=["203.0.113.0/24"],
        is_two_factor_required=True,
        name="Acme",
        organization_id=ORGANIZATION_ID,
        spending_cap_cents=50_000,
    ),
    "organizations.usage.count_apps": lambda hot_code_push: (
        hot_code_push.organizations.usage.count_apps(
            month="2026-09", organization_id=ORGANIZATION_ID
        )
    ),
    "organizations.usage.download_apps_csv": lambda hot_code_push: (
        hot_code_push.organizations.usage.download_apps_csv(
            month="2026-09", organization_id=ORGANIZATION_ID
        )
    ),
    "organizations.usage.get": lambda hot_code_push: hot_code_push.organizations.usage.get(
        month="2026-09", organization_id=ORGANIZATION_ID
    ),
    "organizations.usage.list_apps": lambda hot_code_push: (
        hot_code_push.organizations.usage.list_apps(
            limit=10,
            month="2026-09",
            offset=10,
            organization_id=ORGANIZATION_ID,
            relations=["app"],
        )
    ),
    "organizations.webhooks.count": lambda hot_code_push: (
        hot_code_push.organizations.webhooks.count(organization_id=ORGANIZATION_ID)
    ),
    "organizations.webhooks.create": lambda hot_code_push: (
        hot_code_push.organizations.webhooks.create(
            app_id=APP_ID,
            events=["release.created"],
            format="raw",
            name="Deploys",
            organization_id=ORGANIZATION_ID,
            url="https://example.com/hooks/hotcodepush",
        )
    ),
    "organizations.webhooks.delete": lambda hot_code_push: (
        hot_code_push.organizations.webhooks.delete(
            organization_id=ORGANIZATION_ID, webhook_id=WEBHOOK_ID
        )
    ),
    "organizations.webhooks.deliveries.count": lambda hot_code_push: (
        hot_code_push.organizations.webhooks.deliveries.count(
            created_since=CREATED_SINCE,
            created_until=CREATED_UNTIL,
            organization_id=ORGANIZATION_ID,
            status="failed",
            webhook_id=WEBHOOK_ID,
        )
    ),
    "organizations.webhooks.deliveries.list": lambda hot_code_push: (
        hot_code_push.organizations.webhooks.deliveries.list(
            created_since=CREATED_SINCE,
            created_until=CREATED_UNTIL,
            limit=10,
            offset=10,
            organization_id=ORGANIZATION_ID,
            status="failed",
            webhook_id=WEBHOOK_ID,
        )
    ),
    "organizations.webhooks.deliveries.redeliver": lambda hot_code_push: (
        hot_code_push.organizations.webhooks.deliveries.redeliver(
            delivery_id=DELIVERY_ID, organization_id=ORGANIZATION_ID, webhook_id=WEBHOOK_ID
        )
    ),
    "organizations.webhooks.get": lambda hot_code_push: hot_code_push.organizations.webhooks.get(
        organization_id=ORGANIZATION_ID, webhook_id=WEBHOOK_ID
    ),
    "organizations.webhooks.list": lambda hot_code_push: hot_code_push.organizations.webhooks.list(
        limit=10, offset=10, organization_id=ORGANIZATION_ID
    ),
    "organizations.webhooks.test": lambda hot_code_push: hot_code_push.organizations.webhooks.test(
        organization_id=ORGANIZATION_ID, webhook_id=WEBHOOK_ID
    ),
    "organizations.webhooks.update": lambda hot_code_push: (
        hot_code_push.organizations.webhooks.update(
            app_id=None,
            events=["release.created", "release.paused"],
            is_enabled=True,
            name="Releases",
            organization_id=ORGANIZATION_ID,
            url="https://example.com/hooks/releases",
            webhook_id=WEBHOOK_ID,
        )
    ),
    "users.delete": lambda hot_code_push: hot_code_push.users.delete(
        password=PASSWORD, user_id="me"
    ),
    "users.get": lambda hot_code_push: hot_code_push.users.get(
        relations=["accounts", "members", "members.organization"], user_id="me"
    ),
    "users.password.create": lambda hot_code_push: hot_code_push.users.password.create(
        password=PASSWORD, user_id="me"
    ),
    "users.sessions.delete_many": lambda hot_code_push: hot_code_push.users.sessions.delete_many(
        ids=[SESSION_ID], user_id="me"
    ),
    "users.tokens.delete_many": lambda hot_code_push: hot_code_push.users.tokens.delete_many(
        ids=[TOKEN_ID], user_id="me"
    ),
}

# `/health` is not in the OpenAPI document.
UNDOCUMENTED_RESOURCES = frozenset({"health"})


class SnapshotApi(StubApi):
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


def test_calls_every_operation_the_snapshot_documents() -> None:
    api = SnapshotApi()

    for call in CALLS.values():
        call(api.client)

    called_operation_names = {
        f"{request.method} {resolve_path_template(request.url.path)}" for request in api.requests
    }
    assert resolve_documented_operation_names() - called_operation_names == set()


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
    if isinstance(value, list):
        return [
            undeclared_field
            for index, item in enumerate(value)
            for undeclared_field in resolve_undeclared_fields(item, f"{path}[{index}]")
        ]
    if isinstance(value, dict):
        return [
            undeclared_field
            for key, item in value.items()
            for undeclared_field in resolve_undeclared_fields(item, f"{path}[{key}]")
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
