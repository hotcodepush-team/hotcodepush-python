import httpx
import pytest

from hotcodepush import BinaryCondition, Count, HotCodePushError, Release, ReleaseProgression
from tests.openapi_document import resolve_response_example
from tests.stub_api import StubApi, resolve_sent_json

RELEASE_ROW = resolve_response_example("POST", "/v1/apps/{appId}/channels/{channelId}/releases")
RELEASE_ROWS_WITH_RELATIONS = resolve_response_example(
    "GET", "/v1/apps/{appId}/channels/{channelId}/releases"
)
RELEASES_URL = "https://api.hotcodepush.com/v1/apps/app/channels/channel/releases"


def test_counts_the_release_log_of_the_channel() -> None:
    api = StubApi(httpx.Response(200, json={"count": 3}))

    fetched_count = api.client.apps.channels.releases.count(app_id="app", channel_id="channel")

    assert fetched_count == Count(count=3)
    assert api.sent_methods_and_urls == [f"GET {RELEASES_URL}/count"]


def test_counts_the_releases_of_one_number() -> None:
    api = StubApi(httpx.Response(200, json={"count": 1}))

    api.client.apps.channels.releases.count(app_id="app", channel_id="channel", number=3)

    assert api.sent_methods_and_urls == [f"GET {RELEASES_URL}/count?number=3"]


def test_posts_the_release_to_its_channel_with_its_idempotency_key() -> None:
    api = StubApi(httpx.Response(201, json=RELEASE_ROW))

    created_release = api.client.apps.channels.releases.create(
        app_id="app",
        bundle_id="bundle",
        channel_id="channel",
        idempotency_key="key",
        rollout_percentage=10,
    )

    assert created_release == Release.model_validate(RELEASE_ROW)
    assert api.sent_methods_and_urls == [f"POST {RELEASES_URL}"]
    assert api.last_request.headers["Idempotency-Key"] == "key"
    assert resolve_sent_json(api.last_request) == {"bundleId": "bundle", "rolloutPercentage": 10}


def test_posts_the_conditions_and_the_progression_by_their_api_names() -> None:
    api = StubApi(httpx.Response(201, json=RELEASE_ROW))

    api.client.apps.channels.releases.create(
        app_id="app",
        bundle_id="bundle",
        channel_id="channel",
        conditions=[BinaryCondition(range=">=2.0.0")],
        progression=ReleaseProgression(
            percentages=[25, 50], step_minimum_seconds=3600, step_minimum_update_count=100
        ),
    )

    assert resolve_sent_json(api.last_request) == {
        "bundleId": "bundle",
        "conditions": [{"range": ">=2.0.0", "type": "binary"}],
        "progression": {
            "percentages": [25, 50],
            "stepMinimumSeconds": 3600,
            "stepMinimumUpdateCount": 100,
        },
    }


def test_posts_a_release_of_what_another_channel_serves_with_its_auto_pause_overrides() -> None:
    api = StubApi(httpx.Response(201, json=RELEASE_ROW))

    api.client.apps.channels.releases.create(
        app_id="app",
        channel_id="channel",
        failure_action="revoke",
        failure_minimum_update_count=20,
        failure_threshold_percent=10,
        from_channel_id="source",
    )

    assert resolve_sent_json(api.last_request) == {
        "failureAction": "revoke",
        "failureMinimumUpdateCount": 20,
        "failureThresholdPercent": 10,
        "fromChannelId": "source",
    }


def test_lists_the_release_log_of_the_channel_with_the_linked_rows() -> None:
    api = StubApi(httpx.Response(200, json=RELEASE_ROWS_WITH_RELATIONS))

    fetched_releases = api.client.apps.channels.releases.list(
        app_id="app", channel_id="channel", relations=["bundle", "channel", "releaseCounters"]
    )

    [fetched_release] = fetched_releases
    assert fetched_release.bundle is not None
    assert fetched_release.channel is not None
    assert fetched_release.release_counters is not None
    assert api.sent_methods_and_urls == [
        f"GET {RELEASES_URL}?relations=bundle%2Cchannel%2CreleaseCounters"
    ]


def test_posts_the_bulk_revocation_from_a_release_number() -> None:
    api = StubApi(httpx.Response(200, json=[RELEASE_ROW]))

    revoked_releases = api.client.apps.channels.releases.revoke(
        app_id="app", channel_id="channel", from_number=1
    )

    assert revoked_releases == [Release.model_validate(RELEASE_ROW)]
    assert api.sent_methods_and_urls == [f"POST {RELEASES_URL}/revoke"]
    assert resolve_sent_json(api.last_request) == {"fromNumber": 1}


def test_retries_the_bulk_revocation_when_the_api_is_unavailable() -> None:
    api = StubApi(httpx.Response(503))

    with pytest.raises(HotCodePushError):
        api.client.apps.channels.releases.revoke(
            app_id="app", channel_id="channel", release_ids=["release"]
        )

    assert len(api.requests) == 3
