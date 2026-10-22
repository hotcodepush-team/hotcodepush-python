import httpx

from hotcodepush import OidcConfig, SsoProvider
from tests.openapi_document import resolve_response_example
from tests.stub_api import StubApi, resolve_sent_json

SSO_PROVIDER_ROW = resolve_response_example(
    "GET", "/v1/organizations/{organizationId}/sso-provider"
)
SSO_PROVIDER_URL = "https://api.hotcodepush.com/v1/organizations/organization/sso-provider"


def test_deletes_the_sso_provider() -> None:
    api = StubApi(httpx.Response(204))

    api.client.organizations.sso_provider.delete(organization_id="organization")

    assert api.sent_methods_and_urls == [f"DELETE {SSO_PROVIDER_URL}"]


def test_gets_the_sso_provider() -> None:
    api = StubApi(httpx.Response(200, json=SSO_PROVIDER_ROW))

    fetched_sso_provider = api.client.organizations.sso_provider.get(organization_id="organization")

    assert fetched_sso_provider == SsoProvider.model_validate(SSO_PROVIDER_ROW)
    assert api.sent_methods_and_urls == [f"GET {SSO_PROVIDER_URL}"]


def test_puts_the_domain_and_the_oidc_provider_without_its_unset_fields() -> None:
    api = StubApi(httpx.Response(200, json=SSO_PROVIDER_ROW))

    api.client.organizations.sso_provider.put(
        domain="example.com",
        oidc=OidcConfig(
            client_id="client", client_secret="secret", issuer="https://idp.example.com"
        ),
        organization_id="organization",
    )

    assert api.sent_methods_and_urls == [f"PUT {SSO_PROVIDER_URL}"]
    assert resolve_sent_json(api.last_request) == {
        "domain": "example.com",
        "oidc": {
            "clientId": "client",
            "clientSecret": "secret",
            "issuer": "https://idp.example.com",
        },
    }
