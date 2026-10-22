"""The client against a running API, by hand; see CLAUDE.md for the local setup."""

import hashlib
import os
from collections.abc import Iterator

import pytest

from hotcodepush import App, Channel, HotCodePush, HotCodePushError, ManifestFile, Organization

API_BASE_URL = os.environ.get("HOTCODEPUSH_API_BASE_URL")
INDEX_HTML = b"<h1>Python client</h1>"
PACK_PLACEHOLDER = b"pack placeholder"
"""The API stores a pack without reading it; a real pack is the CLI's tar of the bundle."""
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
    fetched_releases = hot_code_push.apps.channels.releases.list(
        app_id=app.id, channel_id=channel.id, relations=["bundle"]
    )

    assert fetched_releases == []


def test_passes_the_apis_error_through_when_a_bundle_misses_its_files(
    hot_code_push: HotCodePush, app: App
) -> None:
    created_bundle = hot_code_push.apps.bundles.create(
        app_id=app.id,
        files=[
            ManifestFile(
                path="index.html",
                sha256=hashlib.sha256(INDEX_HTML).hexdigest(),
                size_bytes=len(INDEX_HTML),
            )
        ],
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
        "E_UPLOAD_INCOMPLETE",
        409,
    )
    assert raised_after_deletion.value.code == "E_NOT_FOUND"


def test_deletes_the_channel(hot_code_push: HotCodePush, app: App, channel: Channel) -> None:
    hot_code_push.apps.channels.delete(app_id=app.id, channel_id=channel.id)

    with pytest.raises(HotCodePushError) as raised:
        hot_code_push.apps.channels.get(app_id=app.id, channel_id=channel.id)

    assert (raised.value.code, raised.value.status) == ("E_NOT_FOUND", 404)


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

    assert (raised.value.code, raised.value.status) == ("E_NOT_FOUND", 404)
