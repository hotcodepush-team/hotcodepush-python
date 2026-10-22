"""The types every resource method takes or returns, derived from the OpenAPI snapshot.

Fields are snake_case and read the API's camelCase names; a field the API adds later is kept
in `model_extra`, so it never breaks a reader. `relations` embeds linked rows as the optional
fields named after them.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

FailureAction = Literal["none", "notify", "pause", "revoke"]
Framework = Literal["capacitor", "cordova", "expo", "react-native"]
Platform = Literal["android", "ios"]
ReleaseRelation = Literal["bundle", "channel", "releaseCounters"]


class HotCodePushModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, extra="allow", populate_by_name=True)


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


class AttributeCondition(HotCodePushModel):
    """Devices whose attribute `key` holds the value of the SHA-256 `value_sha256`."""

    key: str
    type: Literal["attribute"] = "attribute"
    value_sha256: str


class BinaryCondition(HotCodePushModel):
    """Devices whose binary version lies in `range`, `>=2.0.0` say."""

    range: str
    type: Literal["binary"] = "binary"


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


class BundleSignature(HotCodePushModel):
    """The signature of a bundle's manifest: the signing key's fingerprint and the value."""

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


class Count(HotCodePushModel):
    """What every list's `count` answers: the rows the list's filters match."""

    count: int


class DeviceCondition(HotCodePushModel):
    """Devices whose hashed id is one of `hashed_ids`."""

    hashed_ids: list[str]
    type: Literal["device"] = "device"


class FingerprintCondition(HotCodePushModel):
    """Devices whose binary carries the native `fingerprint`."""

    fingerprint: str
    type: Literal["fingerprint"] = "fingerprint"


class ManifestFile(HotCodePushModel):
    """A file of a bundle's manifest: its path, the SHA-256 of its content and its size."""

    path: str
    sha256: str
    size_bytes: int


class MultipartUpload(HotCodePushModel):
    upload_id: str


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
    """Devices whose operating system version lies in `range`, `>=17` say."""

    range: str
    type: Literal["os"] = "os"


class Release(HotCodePushModel):
    """A release of a bundle in a channel; `bundle`, `channel` and `release_counters` are set
    when `relations` names them.
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
    rollout_percentage: int
    status: Literal["active", "paused", "revoked"]
    step_start_applied_update_count: int
    updated_at: datetime
    window_start_applied_update_count: int
    window_start_failure_count: int


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


class ReleaseProgression(HotCodePushModel):
    """The schedule that raises a release's rollout through `percentages`, a step at a time."""

    percentages: list[int]
    step_minimum_seconds: int
    step_minimum_update_count: int


class UploadedBundlePack(HotCodePushModel):
    size_bytes: int


class UploadedPart(HotCodePushModel):
    """A part of a multipart upload; its `etag` and `part_number` complete the upload."""

    etag: str
    part_number: int


ReleaseCondition = Annotated[
    AttributeCondition | BinaryCondition | DeviceCondition | FingerprintCondition | OsCondition,
    Field(discriminator="type"),
]
"""A condition a device meets to receive a release."""
