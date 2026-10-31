import httpx

from hotcodepush import Usage
from tests.openapi_document import resolve_response_example
from tests.stub_api import StubApi

USAGE_ROW = resolve_response_example("GET", "/v1/organizations/{organizationId}/usage")
USAGE_URL = "https://api.hotcodepush.com/v1/organizations/organization/usage"


def test_gets_the_usage_of_the_organization_in_the_month() -> None:
    api = StubApi(httpx.Response(200, json=USAGE_ROW))

    fetched_usage = api.client.organizations.usage.get(
        month="2026-09", organization_id="organization"
    )

    assert fetched_usage == Usage.model_validate(USAGE_ROW)
    assert api.sent_methods_and_urls == [f"GET {USAGE_URL}?month=2026-09"]
