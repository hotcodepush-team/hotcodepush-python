import httpx

from hotcodepush import Count, Organization
from tests.openapi_document import resolve_response_example
from tests.stub_api import StubApi, resolve_sent_json

ORGANIZATION_ROW = resolve_response_example("GET", "/v1/organizations/{organizationId}")
ORGANIZATIONS_URL = "https://api.hotcodepush.com/v1/organizations"


def test_counts_the_callers_organizations() -> None:
    api = StubApi(httpx.Response(200, json={"count": 3}))

    fetched_count = api.client.organizations.count()

    assert fetched_count == Count(count=3)
    assert api.sent_methods_and_urls == [f"GET {ORGANIZATIONS_URL}/count"]


def test_posts_the_organization_with_its_idempotency_key() -> None:
    api = StubApi(httpx.Response(201, json=ORGANIZATION_ROW))

    created_organization = api.client.organizations.create(idempotency_key="key", name="Acme")

    assert created_organization == Organization.model_validate(ORGANIZATION_ROW)
    assert api.sent_methods_and_urls == [f"POST {ORGANIZATIONS_URL}"]
    assert api.last_request.headers["Idempotency-Key"] == "key"
    assert resolve_sent_json(api.last_request) == {"name": "Acme"}


def test_deletes_the_organization() -> None:
    api = StubApi(httpx.Response(204))

    api.client.organizations.delete(organization_id="organization")

    assert api.sent_methods_and_urls == [f"DELETE {ORGANIZATIONS_URL}/organization"]


def test_gets_the_organization() -> None:
    api = StubApi(httpx.Response(200, json=ORGANIZATION_ROW))

    fetched_organization = api.client.organizations.get(organization_id="organization")

    assert fetched_organization == Organization.model_validate(ORGANIZATION_ROW)
    assert api.sent_methods_and_urls == [f"GET {ORGANIZATIONS_URL}/organization"]


def test_lists_the_organizations_with_limit_and_offset() -> None:
    api = StubApi(httpx.Response(200, json=[ORGANIZATION_ROW]))

    fetched_organizations = api.client.organizations.list(limit=10, offset=20)

    assert fetched_organizations == [Organization.model_validate(ORGANIZATION_ROW)]
    assert api.sent_methods_and_urls == [f"GET {ORGANIZATIONS_URL}?limit=10&offset=20"]


def test_patches_the_organization() -> None:
    api = StubApi(httpx.Response(200, json=ORGANIZATION_ROW))

    api.client.organizations.update(is_two_factor_required=True, organization_id="organization")

    assert api.sent_methods_and_urls == [f"PATCH {ORGANIZATIONS_URL}/organization"]
    assert resolve_sent_json(api.last_request) == {"isTwoFactorRequired": True}
