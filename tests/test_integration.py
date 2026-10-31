# Runs by hand against a local API, set up as CLAUDE.md describes.

import gzip
import hashlib
import io
import os
import re
from collections.abc import Iterator

import pytest

from hotcodepush import App, Channel, HotCodePush, HotCodePushError, ManifestFile, Organization

API_BASE_URL = os.environ.get("HOTCODEPUSH_API_BASE_URL")
INDEX_HTML = b"<h1>Python client</h1>"
MAIN_JS = b'console.log("parts");'
# The API stores a pack without reading it. A real pack is the tar that the CLI builds.
PACK_PLACEHOLDER = b"pack placeholder"
TOKEN = os.environ.get("HOTCODEPUSH_API_TOKEN")

pytestmark = pytest.mark.skipif(
    API_BASE_URL is None, reason="HOTCODEPUSH_API_BASE_URL names no running API"
)


@pytest.fixture(scope="module")
def hot_code_push() -> Iterator[HotCodePush]:
    if not TOKEN:
        raise RuntimeError("HOTCODEPUSH_API_TOKEN must hold the bearer of a verified user.")
    with HotCodePush(TOKEN, base_url=API_BASE_URL or "") as hot_code_push:
        yield hot_code_push


@pytest.fixture(scope="module")
def organization(hot_code_push: HotCodePush) -> Iterator[Organization]:
    created_organization = hot_code_push.organizations.create(name="Python Client Test")
    yield created_organization
    hot_code_push.organizations.delete(organization_id=created_organization.id)


@pytest.fixture(scope="module")
def target_organization(hot_code_push: HotCodePush) -> Iterator[Organization]:
    created_organization = hot_code_push.organizations.create(name="Python Client Test Target")
    yield created_organization
    hot_code_push.organizations.delete(organization_id=created_organization.id)


@pytest.fixture(scope="module")
def app(hot_code_push: HotCodePush, organization: Organization) -> App:
    return hot_code_push.organizations.apps.create(
        framework="capacitor", name="Python Client Demo", organization_id=organization.id
    )


@pytest.fixture(scope="module")
def channel(hot_code_push: HotCodePush, app: App) -> Channel:
    return hot_code_push.apps.channels.create(app_id=app.id, name="staging")


def test_answers_the_health_check(hot_code_push: HotCodePush) -> None:
    hot_code_push.health.get()


def test_gets_lists_and_updates_the_created_organization(
    hot_code_push: HotCodePush, organization: Organization
) -> None:
    fetched_organization = hot_code_push.organizations.get(organization_id=organization.id)
    fetched_organizations = hot_code_push.organizations.list(limit=100)
    updated_organization = hot_code_push.organizations.update(
        name="Python Client Test Renamed", organization_id=organization.id
    )

    assert (fetched_organization.id, fetched_organization.plan) == (organization.id, "free")
    assert organization.id in [listed.id for listed in fetched_organizations]
    assert updated_organization.name == "Python Client Test Renamed"


def test_lists_the_members_with_their_users_and_gets_one(
    hot_code_push: HotCodePush, organization: Organization
) -> None:
    [owner] = hot_code_push.organizations.members.list(
        organization_id=organization.id, relations=["user"]
    )
    fetched_member = hot_code_push.organizations.members.get(
        member_id=owner.id, organization_id=organization.id
    )

    assert owner.user is not None
    assert (fetched_member.id, fetched_member.role) == (owner.id, "owner")


def test_creates_lists_and_withdraws_an_invitation(
    hot_code_push: HotCodePush, organization: Organization
) -> None:
    created_invitation = hot_code_push.organizations.invitations.create(
        email="invitee@example.com", organization_id=organization.id, role="member"
    )
    fetched_invitations = hot_code_push.organizations.invitations.list(
        organization_id=organization.id
    )
    hot_code_push.organizations.invitations.delete(
        invitation_id=created_invitation.id, organization_id=organization.id
    )
    pending_invitations = hot_code_push.invitations.list(relations=["organization"])

    assert created_invitation.status == "pending"
    assert created_invitation.id in [listed.id for listed in fetched_invitations]
    assert all(listed.organization is not None for listed in pending_invitations)


def test_gets_lists_and_updates_the_created_app(
    hot_code_push: HotCodePush, app: App, organization: Organization
) -> None:
    fetched_app = hot_code_push.apps.get(app_id=app.id)
    fetched_apps = hot_code_push.organizations.apps.list(organization_id=organization.id)
    updated_app = hot_code_push.apps.update(
        app_id=app.id, channel_link_template="demo://channels/{channelId}"
    )

    assert (fetched_app.id, fetched_app.name) == (app.id, "Python Client Demo")
    assert [listed.id for listed in fetched_apps] == [app.id]
    assert updated_app.channel_link_template == "demo://channels/{channelId}"


def test_gets_lists_updates_pauses_and_resumes_the_created_channel(
    hot_code_push: HotCodePush, app: App, channel: Channel
) -> None:
    fetched_channel = hot_code_push.apps.channels.get(app_id=app.id, channel_id=channel.id)
    fetched_channels = hot_code_push.apps.channels.list(app_id=app.id)
    updated_channel = hot_code_push.apps.channels.update(
        app_id=app.id, channel_id=channel.id, is_discoverable=True
    )
    paused_channel = hot_code_push.apps.channels.pause(app_id=app.id, channel_id=channel.id)
    resumed_channel = hot_code_push.apps.channels.resume(app_id=app.id, channel_id=channel.id)

    assert (fetched_channel.id, fetched_channel.name) == (channel.id, "staging")
    assert sorted(listed.name for listed in fetched_channels) == ["production", "staging"]
    assert updated_channel.is_discoverable
    assert paused_channel.paused_at is not None
    assert resumed_channel.paused_at is None


def test_lists_no_releases_for_a_new_channel(
    hot_code_push: HotCodePush, app: App, channel: Channel
) -> None:
    fetched_releases = hot_code_push.apps.releases.list(
        app_id=app.id, channel_id=channel.id, relations=["bundle"]
    )

    assert fetched_releases == []


def test_passes_the_apis_error_through_when_there_is_nothing_to_roll_back(
    hot_code_push: HotCodePush, app: App, channel: Channel
) -> None:
    with pytest.raises(HotCodePushError) as raised:
        hot_code_push.apps.channels.rollbacks.create(app_id=app.id, channel_id=channel.id)

    assert (raised.value.code, raised.value.details, raised.value.status) == (
        "validation",
        {"field": "toReleaseId", "rule": "no_earlier_release", "target": "json"},
        400,
    )


def test_passes_the_apis_error_through_when_a_bundle_misses_its_files(
    hot_code_push: HotCodePush, app: App
) -> None:
    created_bundle = hot_code_push.apps.bundles.create(
        app_id=app.id,
        files=[resolve_manifest_file("index.html", INDEX_HTML)],
        platforms=["android"],
        version="1.0.0",
    )
    hot_code_push.apps.bundles.pack.upload(
        app_id=app.id, body=PACK_PLACEHOLDER, bundle_id=created_bundle.id
    )

    with pytest.raises(HotCodePushError) as raised_on_completion:
        hot_code_push.apps.bundles.complete(app_id=app.id, bundle_id=created_bundle.id)
    hot_code_push.apps.bundles.delete(app_id=app.id, bundle_id=created_bundle.id)
    with pytest.raises(HotCodePushError) as raised_after_deletion:
        hot_code_push.apps.bundles.get(app_id=app.id, bundle_id=created_bundle.id)

    assert (raised_on_completion.value.code, raised_on_completion.value.status) == (
        "upload_incomplete",
        409,
    )
    assert raised_after_deletion.value.code == "not_found"


def test_creates_a_bundle_uploads_its_file_and_pack_completes_it_and_reads_its_manifest_hash(
    hot_code_push: HotCodePush, app: App
) -> None:
    index_file = resolve_manifest_file("index.html", INDEX_HTML)
    gzip_bytes = gzip.compress(INDEX_HTML)
    created_bundle = hot_code_push.apps.bundles.create(
        app_id=app.id, files=[index_file], platforms=["android"], version="1.0.0"
    )
    fetched_unstored_files = hot_code_push.apps.bundles.files.list(
        app_id=app.id, bundle_id=created_bundle.id, is_stored=False
    )
    uploaded_file = hot_code_push.apps.files.upload(
        app_id=app.id,
        body=io.BytesIO(gzip_bytes),
        content_length=len(gzip_bytes),
        sha256=index_file.sha256,
    )
    hot_code_push.apps.bundles.pack.upload(
        app_id=app.id, body=PACK_PLACEHOLDER, bundle_id=created_bundle.id
    )
    completed_bundle = hot_code_push.apps.bundles.complete(
        app_id=app.id, bundle_id=created_bundle.id
    )
    fetched_bundle = hot_code_push.apps.bundles.get(app_id=app.id, bundle_id=created_bundle.id)

    assert [listed.sha256 for listed in fetched_unstored_files] == [index_file.sha256]
    assert uploaded_file.sha256 == index_file.sha256
    assert completed_bundle.status == "ready"
    assert re.fullmatch("[0-9a-f]{64}", completed_bundle.manifest_sha256 or "")
    assert fetched_bundle.manifest_sha256 == completed_bundle.manifest_sha256


def test_uploads_a_file_in_parts_and_completes_it(hot_code_push: HotCodePush, app: App) -> None:
    main_file = resolve_manifest_file("main.js", MAIN_JS)
    created_upload = hot_code_push.apps.files.uploads.create(app_id=app.id, sha256=main_file.sha256)
    uploaded_part = hot_code_push.apps.files.uploads.parts.upload(
        app_id=app.id,
        body=gzip.compress(MAIN_JS),
        part_number=1,
        sha256=main_file.sha256,
        upload_id=created_upload.upload_id,
    )

    completed_file = hot_code_push.apps.files.uploads.complete(
        app_id=app.id,
        parts=[uploaded_part],
        sha256=main_file.sha256,
        upload_id=created_upload.upload_id,
    )

    assert completed_file.sha256 == main_file.sha256


def test_aborts_a_multipart_upload(hot_code_push: HotCodePush, app: App) -> None:
    aborted_file = resolve_manifest_file("aborted.js", b"never completed")
    created_upload = hot_code_push.apps.files.uploads.create(
        app_id=app.id, sha256=aborted_file.sha256
    )

    hot_code_push.apps.files.uploads.delete(
        app_id=app.id, sha256=aborted_file.sha256, upload_id=created_upload.upload_id
    )


def test_completes_a_bundle_whose_files_are_stored_lists_it_as_ready_and_deletes_it(
    hot_code_push: HotCodePush, app: App
) -> None:
    created_bundle = hot_code_push.apps.bundles.create(
        app_id=app.id,
        files=[resolve_manifest_file("main.js", MAIN_JS)],
        platforms=["android"],
        version="1.0.1",
    )
    fetched_unstored_files = hot_code_push.apps.bundles.files.list(
        app_id=app.id, bundle_id=created_bundle.id, is_stored=False
    )
    hot_code_push.apps.bundles.pack.upload(
        app_id=app.id, body=PACK_PLACEHOLDER, bundle_id=created_bundle.id
    )
    hot_code_push.apps.bundles.complete(app_id=app.id, bundle_id=created_bundle.id)
    ready_bundles = hot_code_push.apps.bundles.list(app_id=app.id, status="ready")
    hot_code_push.apps.bundles.delete(app_id=app.id, bundle_id=created_bundle.id)

    with pytest.raises(HotCodePushError) as raised:
        hot_code_push.apps.bundles.get(app_id=app.id, bundle_id=created_bundle.id)

    assert fetched_unstored_files == []
    assert created_bundle.id in [listed.id for listed in ready_bundles]
    assert (raised.value.code, raised.value.status) == ("not_found", 404)


def test_creates_a_binary_and_reads_it_with_its_bundle(
    hot_code_push: HotCodePush, app: App
) -> None:
    index_file = resolve_manifest_file("index.html", INDEX_HTML)
    created_binary = hot_code_push.apps.binaries.create(
        app_id=app.id,
        build="1",
        files=[index_file],
        fingerprint=f"fp1:{'a' * 64}",
        platform="android",
        version="1.0.0",
    )
    force_created_binary = hot_code_push.apps.binaries.create(
        app_id=app.id,
        build="1",
        files=[index_file],
        fingerprint=f"fp1:{'b' * 64}",
        force=True,
        platform="android",
        version="1.0.0",
    )
    fetched_binaries = hot_code_push.apps.binaries.list(app_id=app.id)
    fetched_binary = hot_code_push.apps.binaries.get(app_id=app.id, binary_id=created_binary.id)
    fetched_bundle = hot_code_push.apps.bundles.get(
        app_id=app.id, bundle_id=fetched_binary.bundle_id
    )

    assert (force_created_binary.id, force_created_binary.fingerprint) == (
        created_binary.id,
        f"fp1:{'b' * 64}",
    )
    assert [listed.id for listed in fetched_binaries] == [created_binary.id]
    assert fetched_binary.bundle_id == force_created_binary.bundle_id
    assert fetched_bundle.number is None


def test_deletes_the_channel(hot_code_push: HotCodePush, app: App, channel: Channel) -> None:
    hot_code_push.apps.channels.delete(app_id=app.id, channel_id=channel.id)

    with pytest.raises(HotCodePushError) as raised:
        hot_code_push.apps.channels.get(app_id=app.id, channel_id=channel.id)

    assert (raised.value.code, raised.value.status) == ("not_found", 404)


def test_transfers_the_app_to_another_organization(
    hot_code_push: HotCodePush, app: App, target_organization: Organization
) -> None:
    transferred_app = hot_code_push.apps.transfer(
        app_id=app.id, organization_id=target_organization.id
    )

    assert transferred_app.organization_id == target_organization.id


def test_deletes_the_app(hot_code_push: HotCodePush, app: App) -> None:
    hot_code_push.apps.delete(app_id=app.id)

    with pytest.raises(HotCodePushError) as raised:
        hot_code_push.apps.get(app_id=app.id)

    assert (raised.value.code, raised.value.status) == ("not_found", 404)


def resolve_manifest_file(path: str, content: bytes) -> ManifestFile:
    return ManifestFile(
        path=path, sha256=hashlib.sha256(content).hexdigest(), size_bytes=len(content)
    )
