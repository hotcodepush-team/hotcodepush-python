import httpx
import pytest

from hotcodepush import Count, CreatedWebhook, HotCodePushError, Webhook, WebhookDelivery
from tests.openapi_document import resolve_response_example
from tests.stub_api import StubApi, resolve_sent_json

CREATED_WEBHOOK_ROW = resolve_response_example(
    "POST", "/v1/organizations/{organizationId}/webhooks"
)
WEBHOOK_DELIVERY_ROW = resolve_response_example(
    "POST", "/v1/organizations/{organizationId}/webhooks/{webhookId}/test"
)
WEBHOOK_ROW = resolve_response_example(
    "GET", "/v1/organizations/{organizationId}/webhooks/{webhookId}"
)
WEBHOOKS_URL = "https://api.hotcodepush.com/v1/organizations/organization/webhooks"


def test_counts_the_webhooks_of_the_organization() -> None:
    api = StubApi(httpx.Response(200, json={"count": 2}))

    fetched_count = api.client.organizations.webhooks.count(organization_id="organization")

    assert fetched_count == Count(count=2)
    assert api.sent_methods_and_urls == [f"GET {WEBHOOKS_URL}/count"]


def test_posts_the_webhook_without_an_idempotency_key_and_answers_its_secret() -> None:
    api = StubApi(httpx.Response(201, json=CREATED_WEBHOOK_ROW))

    created_webhook = api.client.organizations.webhooks.create(
        events=["release.created"],
        format="raw",
        name="Deploys",
        organization_id="organization",
        url="https://example.com/hooks",
    )

    assert created_webhook == CreatedWebhook.model_validate(CREATED_WEBHOOK_ROW)
    assert created_webhook.secret is not None
    assert api.sent_methods_and_urls == [f"POST {WEBHOOKS_URL}"]
    assert "Idempotency-Key" not in api.last_request.headers
    assert resolve_sent_json(api.last_request) == {
        "events": ["release.created"],
        "format": "raw",
        "name": "Deploys",
        "url": "https://example.com/hooks",
    }


def test_does_not_retry_the_creation_when_the_api_is_unavailable() -> None:
    api = StubApi(httpx.Response(503))

    with pytest.raises(HotCodePushError):
        api.client.organizations.webhooks.create(
            events=["release.created"],
            format="slack",
            name="Deploys",
            organization_id="organization",
            url="https://hooks.slack.com/services/T0/B0/token",
        )

    assert len(api.requests) == 1


def test_deletes_the_webhook() -> None:
    api = StubApi(httpx.Response(204))

    api.client.organizations.webhooks.delete(organization_id="organization", webhook_id="webhook")

    assert api.sent_methods_and_urls == [f"DELETE {WEBHOOKS_URL}/webhook"]


def test_gets_the_webhook() -> None:
    api = StubApi(httpx.Response(200, json=WEBHOOK_ROW))

    fetched_webhook = api.client.organizations.webhooks.get(
        organization_id="organization", webhook_id="webhook"
    )

    assert fetched_webhook == Webhook.model_validate(WEBHOOK_ROW)
    assert api.sent_methods_and_urls == [f"GET {WEBHOOKS_URL}/webhook"]


def test_lists_the_webhooks_of_the_organization() -> None:
    api = StubApi(httpx.Response(200, json=[WEBHOOK_ROW]))

    fetched_webhooks = api.client.organizations.webhooks.list(
        limit=10, organization_id="organization"
    )

    assert fetched_webhooks == [Webhook.model_validate(WEBHOOK_ROW)]
    assert api.sent_methods_and_urls == [f"GET {WEBHOOKS_URL}?limit=10"]


def test_posts_to_test_the_webhook_and_answers_the_settled_delivery() -> None:
    api = StubApi(httpx.Response(201, json=WEBHOOK_DELIVERY_ROW))

    tested_delivery = api.client.organizations.webhooks.test(
        organization_id="organization", webhook_id="webhook"
    )

    assert tested_delivery == WebhookDelivery.model_validate(WEBHOOK_DELIVERY_ROW)
    assert api.sent_methods_and_urls == [f"POST {WEBHOOKS_URL}/webhook/test"]
    assert api.last_request.content == b""


def test_does_not_retry_the_test_when_the_api_is_unavailable() -> None:
    api = StubApi(httpx.Response(503))

    with pytest.raises(HotCodePushError):
        api.client.organizations.webhooks.test(organization_id="organization", webhook_id="webhook")

    assert len(api.requests) == 1


def test_patches_the_webhook() -> None:
    api = StubApi(httpx.Response(200, json=WEBHOOK_ROW))

    api.client.organizations.webhooks.update(
        is_enabled=True, organization_id="organization", webhook_id="webhook"
    )

    assert api.sent_methods_and_urls == [f"PATCH {WEBHOOKS_URL}/webhook"]
    assert resolve_sent_json(api.last_request) == {"isEnabled": True}


def test_patches_the_app_filter_to_null_when_it_is_cleared() -> None:
    api = StubApi(httpx.Response(200, json=WEBHOOK_ROW))

    api.client.organizations.webhooks.update(
        app_id=None, organization_id="organization", webhook_id="webhook"
    )

    assert resolve_sent_json(api.last_request) == {"appId": None}
