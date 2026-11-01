"""The types that resource methods take and return, derived from the OpenAPI snapshot.

Fields are the API's camelCase names in snake_case. A field the API adds later lands in
`model_extra`, so it never breaks a caller. The rows a `relations` argument names fill the
optional fields of the same name.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

AppUsageMonthRelation = Literal["app"]
AuditLogRelation = Literal["app", "user"]
BundleDeltaRelation = Literal["baseBundle"]
DeviceRelation = Literal["channel", "currentRelease"]
FailureAction = Literal["none", "notify", "pause", "revoke"]
Framework = Literal["capacitor", "cordova", "expo", "react_native"]
InvitationRelation = Literal["organization"]
InvitationRole = Literal["admin", "billing", "member"]
"""A role an invitation grants. `owner` is missing, since only a transfer hands it over."""
MemberRelation = Literal["user", "user.accounts"]
NotificationCategory = Literal[
    "account",
    "billing",
    "lifecycle",
    "newsletter",
    "product_alerts",
    "service_notices",
    "spending_alerts",
    "team_activity",
]
NotificationMedium = Literal["email", "in_app"]
NotificationRelation = Literal["app", "channel", "memberUser", "release"]
Platform = Literal["android", "ios"]
ReleaseDeviceEventRelation = Literal["release"]
ReleaseRelation = Literal["bundle", "channel", "releaseCounters"]
Role = Literal["admin", "billing", "member", "owner"]
UserRelation = Literal["accounts", "members", "members.organization"]
WebhookEvent = Literal[
    "app.created",
    "app.deleted",
    "app.restored",
    "app.transferred",
    "app.updated",
    "binary.created",
    "binary.expired",
    "bundle.deleted",
    "bundle.expired",
    "bundle.uploaded",
    "channel.created",
    "channel.deleted",
    "channel.expired",
    "channel.paused",
    "channel.resumed",
    "channel.updated",
    "device.deleted",
    "invitation.accepted",
    "invitation.created",
    "invitation.revoked",
    "member.joined",
    "member.removed",
    "member.role_changed",
    "organization.deleted",
    "organization.dormancy_noticed",
    "organization.fair_use_warning",
    "organization.restored",
    "organization.spending_cap_changed",
    "organization.spending_cap_reached",
    "organization.spending_cap_warning",
    "organization.storage_limit_reached",
    "organization.storage_limit_warning",
    "organization.updated",
    "release.created",
    "release.failure_rate_exceeded",
    "release.paused",
    "release.resumed",
    "release.revoked",
    "release.rollout_changed",
    "release.updated",
    "signing_key.created",
    "signing_key.deleted",
    "subscription.cancellation_scheduled",
    "subscription.ended",
    "subscription.uncanceled",
]
"""An audit type a webhook subscribes to."""


class HotCodePushModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, extra="allow", populate_by_name=True)


class Account(HotCodePushModel):
    """A sign-in identity of a user: `credential` for a password, otherwise the provider."""

    created_at: datetime
    id: str
    provider_id: str
    user_id: str


class AdoptionPoint(HotCodePushModel):
    """A point on a release's adoption curve: a moment and the updates confirmed by then."""

    at: datetime
    confirmed_update_count: int


class App(HotCodePushModel):
    channel_link_template: str | None
    created_at: datetime
    default_channel_id: str | None
    deleted_at: datetime | None
    framework: Framework
    id: str
    name: str
    next_bundle_number: int
    organization_id: str
    updated_at: datetime


class AppFile(HotCodePushModel):
    """A content-addressed file of the app, shared between its bundles."""

    app_id: str
    created_at: datetime
    sha256: str
    size_bytes: int
    updated_at: datetime


class AppUsageMonth(HotCodePushModel):
    """The usage of one live app in a month. `app` is set when `relations` names it."""

    app: NamedEmbed | None = None
    app_id: str
    data_transfer_bytes: int
    month: str
    monthly_active_device_count: int


class AttributeCondition(HotCodePushModel):
    """Devices whose attribute `key` holds `value`."""

    key: str
    type: Literal["attribute"] = "attribute"
    value: str


class Audience(HotCodePushModel):
    """The active devices of a channel, the ones all conditions reach, and the estimate at the
    rollout percent.
    """

    binary_version: list[DeviceCount]
    device_count: int
    estimated_device_count: int
    platform: list[DeviceCount]
    reached_device_count: int
    warnings: list[AudienceWarning]


class AudienceWarning(HotCodePushModel):
    """A problem the release would likely have, based on the device registry and the
    registered binaries.
    """

    code: Literal["fingerprint_unknown", "unsupported_condition_share"]
    details: dict[str, object] | None
    message: str


class AuditLog(HotCodePushModel):
    """A row of the audit log: who did what to which object, and when.

    `app` and `user` are set when `relations` names them and the app or user still exists.
    """

    actor_type: Literal["system", "user"]
    app: NamedEmbed | None = None
    app_id: str | None
    country: str | None
    created_at: datetime
    dispatched_at: datetime | None
    id: str
    ip_address: str | None
    object_id: str | None
    organization_id: str | None
    session_id: str | None
    snapshot: dict[str, object]
    token_id: str | None
    type: str
    updated_at: datetime
    user: EmbeddedUser | None = None
    user_agent: str | None
    user_id: str | None


class Binary(HotCodePushModel):
    """A store build. The fleet statistics count its devices in their `binary` buckets."""

    app_id: str
    build: str
    bundle_id: str
    created_at: datetime
    fingerprint: str | None
    id: str
    platform: Platform
    updated_at: datetime
    version: str


class BinaryCondition(HotCodePushModel):
    """Devices whose binary version lies in `range`, such as `>=2.0.0`."""

    range: str
    type: Literal["binary"] = "binary"


class BinaryCount(HotCodePushModel):
    """The devices of one binary and their newest report.

    `value` is the binary's id. `value`, `platform` and `version` are `None` for builds without
    a registered binary.
    """

    device_count: int
    last_seen_at: datetime
    platform: Platform | None
    value: str | None
    version: str | None


class Bundle(HotCodePushModel):
    app_id: str
    created_at: datetime
    expires_at: datetime | None
    fingerprint: str | None
    framework: Framework
    git_message: str | None
    git_ref: str | None
    git_remote: str | None
    git_sha: str | None
    id: str
    is_git_dirty: bool | None
    manifest_sha256: str | None
    number: int | None
    platforms: list[Platform]
    signature: str | None
    signature_key_id: str | None
    size_bytes: int
    source: Literal["binary", "upload"]
    status: Literal["ready", "uploading"]
    unused_since: datetime | None
    updated_at: datetime
    version: str


class BundleDelta(HotCodePushModel):
    """A delta of a bundle against one base bundle. Its size and patch count are known once it is
    built. `base_bundle` is set when `relations` names it.
    """

    base_bundle: Bundle | None = None
    base_bundle_id: str
    bundle_id: str
    created_at: datetime
    patch_count: int | None
    requested_at: datetime
    size_bytes: int | None
    status: Literal["built", "failed", "requested"]
    updated_at: datetime


class BundleFile(HotCodePushModel):
    """A file a bundle lists. `stored_at` is when the app stored a file with its hash."""

    bundle_id: str
    created_at: datetime
    path: str
    sha256: str
    size_bytes: int
    stored_at: datetime | None
    updated_at: datetime


class BundleSignature(HotCodePushModel):
    """The signature of a bundle manifest: the key id of the signing key and the value."""

    key_id: str
    value: str


class Channel(HotCodePushModel):
    app_id: str
    created_at: datetime
    expires_at: datetime | None
    failure_action: FailureAction | None
    failure_minimum_update_count: int | None
    failure_threshold_percent: int | None
    id: str
    is_discoverable: bool
    is_protected: bool
    name: str
    next_release_number: int
    paused_at: datetime | None
    updated_at: datetime


class Checkout(HotCodePushModel):
    """The URL of the Polar checkout to open."""

    url: str


class Count(HotCodePushModel):
    """The answer of every `count` method: the number of rows the filters match."""

    count: int


class CustomerPortalSession(HotCodePushModel):
    """The URL of the Polar customer portal to open."""

    url: str


class DailyUpdateCounts(HotCodePushModel):
    """The updates of one day and the active devices of the channel that day.

    The active devices are the denominator of the adoption rate.
    """

    active_device_count: int | None
    confirmed_update_count: int
    day: date
    failed_update_count: int
    rolled_back_update_count: int


class Device(HotCodePushModel):
    """A device of the registry, as of its last report.

    `channel` and `current_release` are set when `relations` names them.
    """

    app_id: str
    attributes: dict[str, str]
    binary_build: str
    binary_version: str
    channel: Channel | None = None
    channel_id: str | None
    channel_source: Literal["config", "runtime"]
    country: str | None
    created_at: datetime
    current_release: Release | None = None
    current_release_id: str | None
    device_id: str
    embedded_bundle_id: str | None
    fingerprint: str | None
    last_seen_at: datetime
    os_version: str
    platform: Platform
    sdk_version: str
    updated_at: datetime


class DeviceCondition(HotCodePushModel):
    """Devices whose id is one of `ids`, at most 500."""

    ids: list[str]
    type: Literal["device"] = "device"


class DeviceCount(HotCodePushModel):
    """One value of a dimension and the number of devices that report it."""

    device_count: int
    value: str | None


class EmbeddedRelease(HotCodePushModel):
    """A release embedded in a notification: the id and the number, since a release has no
    name.
    """

    id: str
    number: int


class EmbeddedUser(HotCodePushModel):
    """A user embedded in a member or audit log row: what a colleague may see.

    `accounts` is set when `relations` names `user.accounts`.
    """

    accounts: list[Account] | None = None
    created_at: datetime
    email: str
    email_verified: bool
    id: str
    image: str | None
    name: str
    two_factor_enabled: bool
    updated_at: datetime


class FingerprintCondition(HotCodePushModel):
    """Devices whose binary carries the native `fingerprint`."""

    fingerprint: str
    type: Literal["fingerprint"] = "fingerprint"


class FleetStatistics(HotCodePushModel):
    """The devices seen in the last thirty days, with counts per dimension, most common first.

    `current_device_count` counts the devices on the newest active release of their channel.
    """

    binary: list[BinaryCount]
    binary_version: list[DeviceCount]
    channel: list[DeviceCount]
    country: list[DeviceCount]
    current_device_count: int
    device_count: int
    os_version: list[OsVersionCount]
    platform: list[DeviceCount]
    release: list[ReleaseCount]
    sdk_version: list[DeviceCount]


class Invitation(HotCodePushModel):
    """An invitation to an organization.

    `organization` is set on the caller's own invitations when `relations` names it.
    """

    created_at: datetime
    email: str
    expires_at: datetime
    id: str
    inviter_id: str
    organization: NamedEmbed | None = None
    organization_id: str
    role: InvitationRole
    status: Literal["accepted", "pending"]
    updated_at: datetime


class Limit(HotCodePushModel):
    """A limit in effect: its value, the plan default and whether the value overrides it."""

    default: int
    is_overridden: bool
    value: int


class ManifestFile(HotCodePushModel):
    """A file of a bundle manifest: its path, the SHA-256 hash of its content and its size."""

    path: str
    sha256: str
    size_bytes: int


class Member(HotCodePushModel):
    """A member of an organization. `organization` and `user` are set when `relations` names
    them.
    """

    created_at: datetime
    id: str
    last_seen_at: datetime | None
    organization: Organization | None = None
    organization_id: str
    role: Role
    updated_at: datetime
    user: EmbeddedUser | None = None
    user_id: str


class MultipartUpload(HotCodePushModel):
    upload_id: str


class NamedEmbed(HotCodePushModel):
    """The id and name of a row embedded through `relations`: an app, an organization, a
    channel or a member user.
    """

    id: str
    name: str


class Notification(HotCodePushModel):
    """An in-app notification for the caller. `organization_id` is `None` when it is about the
    caller's account. `organization_name` names the organization of a deletion notice, which
    outlives it.

    `app`, `channel`, `member_user` and `release` are set when `relations` names them, and are
    `None` once the row is deleted.
    """

    app: NamedEmbed | None = None
    app_id: str | None
    channel: NamedEmbed | None = None
    channel_id: str | None
    created_at: datetime
    id: str
    member_user: NamedEmbed | None = None
    member_user_id: str | None
    organization_id: str | None
    organization_name: str | None
    read_at: datetime | None
    release: EmbeddedRelease | None = None
    release_id: str | None
    type: str
    updated_at: datetime
    user_id: str


class NotificationPreference(HotCodePushModel):
    """Whether the caller receives the notifications of one category through one medium.

    It applies to the caller's account, or to one membership when `organization_id` is set.
    """

    category: NotificationCategory
    is_enabled: bool
    medium: NotificationMedium
    organization_id: str | None


class OidcConfig(HotCodePushModel):
    """The OpenID Connect provider for the SSO of an organization. A `None` field is not sent."""

    client_id: str
    client_secret: str
    discovery_endpoint: str | None = None
    issuer: str
    scopes: list[str] | None = None


class Organization(HotCodePushModel):
    app_count_limit: int | None
    capped_at: datetime | None
    channel_count_per_app_limit: int | None
    country_allowlist: list[str] | None
    created_at: datetime
    current_period_ends_at: datetime | None
    data_transfer_bytes_per_monthly_active_device_limit: int | None
    deleted_at: datetime | None
    enterprise_monthly_active_device_count_limit: int | None
    file_count_per_bundle_limit: int | None
    final_period_ends_at: datetime | None
    id: str
    ip_allowlist: list[str] | None
    is_two_factor_required: bool
    last_spending_cap_reached_sent_at: datetime | None
    last_spending_cap_warning_sent_at: datetime | None
    last_storage_limit_reached_sent_at: datetime | None
    last_storage_warning_sent_at: datetime | None
    member_count_limit: int | None
    name: str
    past_due_at: datetime | None
    plan: Literal["enterprise", "free", "pay_as_you_go"]
    region: str
    release_count_per_app_per_day_limit: int | None
    reported_billable_device_count: int
    reported_billable_device_count_hour: datetime | None
    reported_billable_device_count_month: date | None
    retention_days: int | None
    spending_cap_cents: int
    storage_bytes: int
    storage_bytes_limit: int | None
    subscription_provider: Literal["polar"] | None
    subscription_status: str | None
    unsent_billable_device_count: int
    updated_at: datetime


class OsCondition(HotCodePushModel):
    """Devices whose operating system version lies in `range`, such as `>=17`."""

    range: str
    type: Literal["os"] = "os"


class OsVersionCount(HotCodePushModel):
    """The devices on one operating system version of one platform."""

    device_count: int
    platform: Platform
    value: str | None


class ReasonCount(HotCodePushModel):
    """A reason the devices reported and the number of events that gave it."""

    event_count: int
    reason: str


class Release(HotCodePushModel):
    """A release of a bundle in a channel.

    `bundle`, `channel` and `release_counters` are set when `relations` names them.
    """

    auto_paused_at: datetime | None
    bundle: Bundle | None = None
    bundle_id: str
    channel: Channel | None = None
    channel_id: str
    conditions: list[ReleaseCondition]
    created_at: datetime
    created_from_release_id: str | None
    failure_action: FailureAction | None
    failure_minimum_update_count: int | None
    failure_notified_at: datetime | None
    failure_threshold_percent: int | None
    id: str
    is_mandatory: bool
    live_at: datetime | None
    notes: str | None
    number: int
    paused_at: datetime | None
    progression: ReleaseProgression | None
    progression_step_started_at: datetime | None
    purged_at: datetime | None
    release_counters: ReleaseCounters | None = None
    rolled_back_from_release_id: str | None
    rollout_percent: int
    status: Literal["active", "paused", "revoked"]
    step_start_applied_update_count: int
    updated_at: datetime
    window_start_applied_update_count: int
    window_start_failed_update_count: int


class ReleaseAdoption(HotCodePushModel):
    """The adoption curve of a live release since it went live.

    It includes the moments the release reached half and nine tenths of the active devices.
    """

    adoption: list[AdoptionPoint]
    channel_id: str
    live_at: datetime
    number: int
    release_id: str
    time_to_adoption: TimeToAdoption


class ReleaseCount(HotCodePushModel):
    """The devices of one release. `value` is the release id.

    `value`, `number` and `channel_id` are `None` for devices on the embedded bundle.
    """

    channel_id: str | None
    device_count: int
    number: int | None
    value: str | None


class ReleaseCounters(HotCodePushModel):
    applied_update_count: int
    confirmed_update_count: int
    crash_failure_count: int
    created_at: datetime
    download_failure_count: int
    readiness_timeout_failure_count: int
    release_id: str
    reported_failure_count: int
    updated_at: datetime
    verification_failure_count: int


class ReleaseDeviceEvent(HotCodePushModel):
    """The first event of each type that a device reported on a release, with the reason of a
    failure. `release` is set when `relations` names it.
    """

    created_at: datetime
    device_id: str
    reason: str | None
    release: Release | None = None
    release_id: str
    type: Literal["applied", "checked", "confirmed", "failed"]
    updated_at: datetime


class ReleaseProgression(HotCodePushModel):
    """A schedule that raises the rollout of a release through `rollout_percents`, one step at
    a time.
    """

    rollout_percents: list[int]
    step_minimum_seconds: int
    step_minimum_update_count: int


class SamlConfig(HotCodePushModel):
    """The SAML provider for the SSO of an organization.

    Set either `metadata`, or `cert` with `entity_id`. A `None` field is not sent.
    """

    cert: str | None = None
    entity_id: str | None = None
    entry_point: str
    issuer: str
    metadata: str | None = None


class SigningKey(HotCodePushModel):
    """A public key that verifies the bundles of an app. Its `key_id` is the `sha256:` digest
    that a signature names.
    """

    app_id: str
    created_at: datetime
    id: str
    key_id: str
    public_key: str
    updated_at: datetime


class SsoProvider(HotCodePushModel):
    """The SSO provider of an organization. The OIDC and SAML configs are write-only.

    `domain_verified` is set once the TXT record `_hotcodepush-sso-{providerId}.{domain}`
    carries the `domain_verification_token`.
    """

    created_at: datetime
    domain: str
    domain_verification_token: str | None
    domain_verified: bool
    id: str
    issuer: str
    organization_id: str
    provider_id: str
    type: Literal["oidc", "saml"]
    updated_at: datetime
    user_id: str | None


class TimeToAdoption(HotCodePushModel):
    """When a release reached half and nine tenths of the active devices of its channel. Each
    is `None` until it happens.
    """

    percent50_at: datetime | None
    percent90_at: datetime | None


class UpdateStatistics(HotCodePushModel):
    """The updates per day of a period, the adoption curves of the newest live releases and
    the reasons the devices reported.
    """

    days: list[DailyUpdateCounts]
    failure_reasons: list[ReasonCount]
    releases: list[ReleaseAdoption]
    skipped_reasons: list[ReasonCount]


class UploadedBundlePack(HotCodePushModel):
    size_bytes: int


class UploadedPart(HotCodePushModel):
    """A part of a multipart upload. Pass its `etag` and `part_number` to complete the upload."""

    etag: str
    part_number: int


class Usage(HotCodePushModel):
    """The monthly active devices and data transfer of an organization in `month`, summed over
    its apps. `month` is `YYYY-MM`.
    """

    data_transfer_bytes: int
    month: str
    monthly_active_device_count: int


class UsageDay(HotCodePushModel):
    """The checks and data transfer of one day, and the bytes the devices reported downloading."""

    check_count: int
    data_transfer_bytes: int
    day: date
    device_download_bytes: int


class UsageMonth(HotCodePushModel):
    """The monthly active devices and data transfer of one month, as the invoice shows them.
    `month` is `YYYY-MM`.
    """

    data_transfer_bytes: int
    month: str
    monthly_active_device_count: int


class UsageStatistics(HotCodePushModel):
    """The monthly active devices and data transfer of each month in a period, and the checks,
    data transfer and device downloads per day.
    """

    days: list[UsageDay]
    months: list[UsageMonth]


class User(HotCodePushModel):
    """The caller. `accounts` and `members` are set when `relations` names them."""

    accounts: list[Account] | None = None
    banned_at: datetime | None
    created_at: datetime
    deleted_at: datetime | None
    discovery_source: (
        Literal[
            "ai_assistant",
            "blog_or_article",
            "friend_or_colleague",
            "github",
            "linkedin",
            "other",
            "reddit",
            "search_engine",
            "x_twitter",
            "youtube",
        ]
        | None
    )
    email: str
    email_verified: bool
    id: str
    image: str | None
    intended_framework: Literal["capacitor", "cordova", "expo", "react_native", "unsure"] | None
    job_role: (
        Literal[
            "cto_or_founder",
            "developer",
            "freelancer_or_agency",
            "manager_or_lead",
            "other",
            "student_or_hobbyist",
        ]
        | None
    )
    last_seen_at: datetime
    locale: str | None
    members: list[Member] | None = None
    name: str
    time_format: Literal["12h", "24h"] | None
    time_zone: str | None
    two_factor_enabled: bool
    updated_at: datetime


class Webhook(HotCodePushModel):
    """An outbound webhook for the audit `events` it subscribes to.

    `format` is `raw` for the JSON payload, or `slack`, `discord` or `teams` for a chat message.
    `app_id` is `None` for the events of every app and of the organization. `is_enabled` turns
    off after fifty failed deliveries in a row.
    """

    app_id: str | None
    consecutive_failure_count: int
    created_at: datetime
    events: list[str]
    format: Literal["discord", "raw", "slack", "teams"]
    id: str
    is_enabled: bool
    name: str
    organization_id: str
    updated_at: datetime
    url: str


# Out of the alphabetical order: a subclass follows its base.
class CreatedWebhook(Webhook):
    """A created webhook with its signing `secret`, returned only this once.

    `secret` is `None` for a chat format, whose URL carries the token.
    """

    secret: str | None


class WebhookDelivery(HotCodePushModel):
    """One event sent to a webhook, with its attempts.

    `type` is the audit type or `webhook.test`. `response_code` and `response_body` are from the
    last attempt, and the body is cut at 4,096 characters. `next_attempt_at` is set while the
    queue retries the delivery.
    """

    attempt_count: int
    audit_row_id: str | None
    created_at: datetime
    id: str
    next_attempt_at: datetime | None
    response_body: str | None
    response_code: int | None
    status: Literal["failed", "pending", "succeeded"]
    type: str
    updated_at: datetime
    webhook_id: str


ReleaseCondition = Annotated[
    AttributeCondition | BinaryCondition | DeviceCondition | FingerprintCondition | OsCondition,
    Field(discriminator="type"),
]
"""A condition a device meets to receive a release."""
