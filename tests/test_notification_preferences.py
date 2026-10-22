import httpx

from hotcodepush import NotificationPreference
from tests.openapi_document import resolve_response_example
from tests.stub_api import StubApi, resolve_sent_json

NOTIFICATION_PREFERENCE_ROW = resolve_response_example("PATCH", "/v1/notification-preferences")
NOTIFICATION_PREFERENCES_URL = "https://api.hotcodepush.com/v1/notification-preferences"


def test_lists_the_preferences_of_the_caller_in_the_organization() -> None:
    api = StubApi(httpx.Response(200, json=[NOTIFICATION_PREFERENCE_ROW]))

    fetched_notification_preferences = api.client.notification_preferences.list(
        organization_id="organization"
    )

    assert fetched_notification_preferences == [
        NotificationPreference.model_validate(NOTIFICATION_PREFERENCE_ROW)
    ]
    assert api.sent_methods_and_urls == [
        f"GET {NOTIFICATION_PREFERENCES_URL}?organizationId=organization"
    ]


def test_patches_one_category_and_medium() -> None:
    api = StubApi(httpx.Response(200, json=NOTIFICATION_PREFERENCE_ROW))

    updated_notification_preference = api.client.notification_preferences.update(
        category="product_alerts", is_enabled=False, medium="email", organization_id="organization"
    )

    assert updated_notification_preference == NotificationPreference.model_validate(
        NOTIFICATION_PREFERENCE_ROW
    )
    assert api.sent_methods_and_urls == [f"PATCH {NOTIFICATION_PREFERENCES_URL}"]
    assert resolve_sent_json(api.last_request) == {
        "category": "product_alerts",
        "isEnabled": False,
        "medium": "email",
        "organizationId": "organization",
    }
