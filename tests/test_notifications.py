import httpx

from hotcodepush import Count, Notification
from tests.openapi_document import resolve_response_example
from tests.stub_api import StubApi, resolve_sent_json

NOTIFICATION_ROW = resolve_response_example("PATCH", "/v1/notifications/{notificationId}")
NOTIFICATION_ROWS_WITH_RELATIONS = resolve_response_example("GET", "/v1/notifications")
NOTIFICATIONS_URL = "https://api.hotcodepush.com/v1/notifications"


def test_counts_the_unread_notifications_of_the_caller() -> None:
    api = StubApi(httpx.Response(200, json={"count": 3}))

    fetched_count = api.client.notifications.count(is_read=False)

    assert fetched_count == Count(count=3)
    assert api.sent_methods_and_urls == [f"GET {NOTIFICATIONS_URL}/count?isRead=false"]


def test_lists_the_unread_notifications_of_the_caller() -> None:
    api = StubApi(httpx.Response(200, json=[NOTIFICATION_ROW]))

    fetched_notifications = api.client.notifications.list(is_read=False, limit=10)

    assert fetched_notifications == [Notification.model_validate(NOTIFICATION_ROW)]
    assert api.sent_methods_and_urls == [f"GET {NOTIFICATIONS_URL}?isRead=false&limit=10"]


def test_lists_the_notifications_with_their_release_when_the_release_relation_is_set() -> None:
    api = StubApi(httpx.Response(200, json=NOTIFICATION_ROWS_WITH_RELATIONS))

    fetched_notifications = api.client.notifications.list(relations=["release"])

    [fetched_notification] = fetched_notifications
    assert fetched_notification.release is not None
    assert api.sent_methods_and_urls == [f"GET {NOTIFICATIONS_URL}?relations=release"]


def test_patches_the_notification_read() -> None:
    api = StubApi(httpx.Response(200, json=NOTIFICATION_ROW))

    updated_notification = api.client.notifications.update(
        is_read=True, notification_id="notification"
    )

    assert updated_notification == Notification.model_validate(NOTIFICATION_ROW)
    assert api.sent_methods_and_urls == [f"PATCH {NOTIFICATIONS_URL}/notification"]
    assert resolve_sent_json(api.last_request) == {"isRead": True}


def test_patches_every_notification_of_the_caller_read() -> None:
    api = StubApi(httpx.Response(204))

    api.client.notifications.update_many(is_read=True)

    assert api.sent_methods_and_urls == [f"PATCH {NOTIFICATIONS_URL}"]
    assert resolve_sent_json(api.last_request) == {"isRead": True}
