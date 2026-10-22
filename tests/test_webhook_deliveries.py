from datetime import UTC, datetime

import httpx
import pytest

from hotcodepush import Count, HotCodePushError, WebhookDelivery
from tests.openapi_document import resolve_response_example
from tests.stub_api import StubApi

DELIVERIES_URL = (
    "https://api.hotcodepush.com/v1/organizations/organization/webhooks/webhook/deliveries"
)
WEBHOOK_DELIVERY_ROW = resolve_response_example(
    "POST",
    "/v1/organizations/{organizationId}/webhooks/{webhookId}/deliveries/{deliveryId}/redeliver",
)


def test_counts_the_deliveries_of_the_webhook_under_the_filters() -> None:
    api = StubApi(httpx.Response(200, json={"count": 4}))

    fetched_count = api.client.organizations.webhooks.deliveries.count(
        created_since=datetime(2026, 10, 1, tzinfo=UTC),
        organization_id="organization",
        status="failed",
        webhook_id="webhook",
    )

    assert fetched_count == Count(count=4)
    assert api.sent_methods_and_urls == [
        f"GET {DELIVERIES_URL}/count?createdSince=2026-10-01T00%3A00%3A00.000Z&status=failed"
    ]


def test_lists_the_deliveries_of_the_webhook_under_the_filters() -> None:
    api = StubApi(httpx.Response(200, json=[WEBHOOK_DELIVERY_ROW]))

    fetched_deliveries = api.client.organizations.webhooks.deliveries.list(
        created_until=datetime(2026, 10, 20, tzinfo=UTC),
        limit=10,
        organization_id="organization",
        status="pending",
        webhook_id="webhook",
    )

    assert fetched_deliveries == [WebhookDelivery.model_validate(WEBHOOK_DELIVERY_ROW)]
    assert api.sent_methods_and_urls == [
        f"GET {DELIVERIES_URL}?createdUntil=2026-10-20T00%3A00%3A00.000Z&limit=10&status=pending"
    ]


def test_posts_to_redeliver_the_delivery_and_answers_it_settled() -> None:
    api = StubApi(httpx.Response(200, json=WEBHOOK_DELIVERY_ROW))

    redelivered_delivery = api.client.organizations.webhooks.deliveries.redeliver(
        delivery_id="delivery", organization_id="organization", webhook_id="webhook"
    )

    assert redelivered_delivery == WebhookDelivery.model_validate(WEBHOOK_DELIVERY_ROW)
    assert api.sent_methods_and_urls == [f"POST {DELIVERIES_URL}/delivery/redeliver"]
    assert api.last_request.content == b""


def test_does_not_retry_the_redelivery_when_the_api_is_unavailable() -> None:
    api = StubApi(httpx.Response(503))

    with pytest.raises(HotCodePushError):
        api.client.organizations.webhooks.deliveries.redeliver(
            delivery_id="delivery", organization_id="organization", webhook_id="webhook"
        )

    assert len(api.requests) == 1
