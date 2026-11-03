import httpx
import pytest

from hotcodepush import Delivery, HotCodePushError, TelemetryExport
from tests.openapi_document import resolve_response_example
from tests.stub_api import StubApi, resolve_sent_json

TELEMETRY_EXPORT_DELIVERY_ROW = resolve_response_example(
    method="POST",
    template="/v1/organizations/{organizationId}/telemetry-export/deliveries/{deliveryId}/redeliver",
)
TELEMETRY_EXPORT_ROW = resolve_response_example(
    method="GET", template="/v1/organizations/{organizationId}/telemetry-export"
)
TELEMETRY_EXPORT_URL = "https://api.hotcodepush.com/v1/organizations/organization/telemetry-export"


def test_deletes_the_telemetry_export() -> None:
    api = StubApi(httpx.Response(204))

    api.client.organizations.telemetry_export.delete(organization_id="organization")

    assert api.sent_methods_and_urls == [f"DELETE {TELEMETRY_EXPORT_URL}"]


def test_gets_the_telemetry_export() -> None:
    api = StubApi(httpx.Response(200, json=TELEMETRY_EXPORT_ROW))

    fetched_telemetry_export = api.client.organizations.telemetry_export.get(
        organization_id="organization"
    )

    assert fetched_telemetry_export == TelemetryExport.model_validate(TELEMETRY_EXPORT_ROW)
    assert api.sent_methods_and_urls == [f"GET {TELEMETRY_EXPORT_URL}"]


def test_puts_the_url_the_headers_and_the_signals() -> None:
    api = StubApi(httpx.Response(201, json=TELEMETRY_EXPORT_ROW))

    api.client.organizations.telemetry_export.set(
        headers={"Authorization": "Bearer example-token"},
        organization_id="organization",
        signals=["logs"],
        url="https://otlp.example.com",
    )

    assert api.sent_methods_and_urls == [f"PUT {TELEMETRY_EXPORT_URL}"]
    assert resolve_sent_json(api.last_request) == {
        "headers": {"Authorization": "Bearer example-token"},
        "signals": ["logs"],
        "url": "https://otlp.example.com",
    }


def test_posts_to_test_the_telemetry_export_and_answers_the_settled_deliveries() -> None:
    api = StubApi(httpx.Response(201, json=[TELEMETRY_EXPORT_DELIVERY_ROW]))

    tested_deliveries = api.client.organizations.telemetry_export.test(
        organization_id="organization"
    )

    assert tested_deliveries == [Delivery.model_validate(TELEMETRY_EXPORT_DELIVERY_ROW)]
    assert api.sent_methods_and_urls == [f"POST {TELEMETRY_EXPORT_URL}/test"]
    assert api.last_request.content == b""


def test_does_not_retry_the_test_when_the_api_is_unavailable() -> None:
    api = StubApi(httpx.Response(503))

    with pytest.raises(HotCodePushError):
        api.client.organizations.telemetry_export.test(organization_id="organization")

    assert len(api.requests) == 1


def test_patches_the_telemetry_export_off() -> None:
    api = StubApi(httpx.Response(200, json=TELEMETRY_EXPORT_ROW))

    api.client.organizations.telemetry_export.update(
        is_enabled=False, organization_id="organization"
    )

    assert api.sent_methods_and_urls == [f"PATCH {TELEMETRY_EXPORT_URL}"]
    assert resolve_sent_json(api.last_request) == {"isEnabled": False}
