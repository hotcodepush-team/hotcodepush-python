import httpx
import pytest

from hotcodepush import Count, HotCodePushError, Release
from tests.openapi_document import resolve_response_example
from tests.stub_api import StubApi, resolve_sent_json

RELEASE_ROW = resolve_response_example("PATCH", "/v1/apps/{appId}/releases/{releaseId}")
RELEASE_ROW_WITH_RELATIONS = resolve_response_example(
    "GET", "/v1/apps/{appId}/releases/{releaseId}"
)
RELEASE_ROWS_WITH_RELATIONS = resolve_response_example("GET", "/v1/apps/{appId}/releases")
RELEASES_URL = "https://api.hotcodepush.com/v1/apps/app/releases"


def test_counts_the_releases_of_the_app_filtered_by_channel_and_status() -> None:
    api = StubApi(httpx.Response(200, json={"count": 3}))

    fetched_count = api.client.apps.releases.count(
        app_id="app", channel_id="channel", status="paused"
    )

    assert fetched_count == Count(count=3)
    assert api.sent_methods_and_urls == [
        f"GET {RELEASES_URL}/count?channelId=channel&status=paused"
    ]


def test_counts_the_releases_of_one_number_in_the_channel() -> None:
    api = StubApi(httpx.Response(200, json={"count": 1}))

    api.client.apps.releases.count(app_id="app", channel_id="channel", number=3)

    assert api.sent_methods_and_urls == [f"GET {RELEASES_URL}/count?channelId=channel&number=3"]


def test_gets_the_release_with_the_linked_rows() -> None:
    api = StubApi(httpx.Response(200, json=RELEASE_ROW_WITH_RELATIONS))

    fetched_release = api.client.apps.releases.get(
        app_id="app", relations=["releaseCounters"], release_id="release"
    )

    assert fetched_release.release_counters is not None
    assert api.sent_methods_and_urls == [f"GET {RELEASES_URL}/release?relations=releaseCounters"]


def test_lists_the_releases_of_the_app_filtered_by_channel_and_status() -> None:
    api = StubApi(httpx.Response(200, json=[RELEASE_ROW]))

    fetched_releases = api.client.apps.releases.list(
        app_id="app", channel_id="channel", status="paused"
    )

    assert fetched_releases == [Release.model_validate(RELEASE_ROW)]
    assert api.sent_methods_and_urls == [f"GET {RELEASES_URL}?channelId=channel&status=paused"]


def test_lists_the_release_of_one_number_in_the_channel_with_the_linked_rows() -> None:
    api = StubApi(httpx.Response(200, json=RELEASE_ROWS_WITH_RELATIONS))

    fetched_releases = api.client.apps.releases.list(
        app_id="app",
        channel_id="channel",
        number=3,
        relations=["bundle", "channel", "releaseCounters"],
    )

    [fetched_release] = fetched_releases
    assert fetched_release.bundle is not None
    assert fetched_release.channel is not None
    assert fetched_release.release_counters is not None
    assert api.sent_methods_and_urls == [
        f"GET {RELEASES_URL}?channelId=channel&number=3"
        "&relations=bundle%2Cchannel%2CreleaseCounters"
    ]


def test_posts_to_pause_the_release() -> None:
    api = StubApi(httpx.Response(200, json=RELEASE_ROW))

    paused_release = api.client.apps.releases.pause(app_id="app", release_id="release")

    assert paused_release == Release.model_validate(RELEASE_ROW)
    assert api.sent_methods_and_urls == [f"POST {RELEASES_URL}/release/pause"]
    assert api.last_request.content == b""


def test_retries_the_pause_when_the_api_is_unavailable() -> None:
    api = StubApi(httpx.Response(503))

    with pytest.raises(HotCodePushError):
        api.client.apps.releases.pause(app_id="app", release_id="release")

    assert len(api.requests) == 3


def test_posts_to_resume_the_release() -> None:
    api = StubApi(httpx.Response(200, json=RELEASE_ROW))

    api.client.apps.releases.resume(app_id="app", release_id="release")

    assert api.sent_methods_and_urls == [f"POST {RELEASES_URL}/release/resume"]
    assert api.last_request.content == b""


def test_retries_the_resume_when_the_api_is_unavailable() -> None:
    api = StubApi(httpx.Response(503))

    with pytest.raises(HotCodePushError):
        api.client.apps.releases.resume(app_id="app", release_id="release")

    assert len(api.requests) == 3


def test_posts_to_revoke_the_release() -> None:
    api = StubApi(httpx.Response(200, json=RELEASE_ROW))

    api.client.apps.releases.revoke(app_id="app", release_id="release")

    assert api.sent_methods_and_urls == [f"POST {RELEASES_URL}/release/revoke"]
    assert api.last_request.content == b""


def test_does_not_retry_the_revoke_when_the_api_is_unavailable() -> None:
    api = StubApi(httpx.Response(503))

    with pytest.raises(HotCodePushError):
        api.client.apps.releases.revoke(app_id="app", release_id="release")

    assert len(api.requests) == 1


def test_patches_the_release() -> None:
    api = StubApi(httpx.Response(200, json=RELEASE_ROW))

    api.client.apps.releases.update(app_id="app", release_id="release", rollout_percent=50)

    assert api.sent_methods_and_urls == [f"PATCH {RELEASES_URL}/release"]
    assert resolve_sent_json(api.last_request) == {"rolloutPercent": 50}


def test_patches_the_progression_to_null_when_it_is_stopped() -> None:
    api = StubApi(httpx.Response(200, json=RELEASE_ROW))

    api.client.apps.releases.update(app_id="app", progression=None, release_id="release")

    assert resolve_sent_json(api.last_request) == {"progression": None}
