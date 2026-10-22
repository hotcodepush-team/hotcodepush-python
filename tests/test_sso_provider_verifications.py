import httpx
import pytest

from hotcodepush import HotCodePushError, SsoProvider
from tests.openapi_document import resolve_response_example
from tests.stub_api import StubApi

SSO_PROVIDER_ROW = resolve_response_example(
    "POST", "/v1/organizations/{organizationId}/sso-provider/verifications"
)


def test_posts_to_verify_the_domain() -> None:
    api = StubApi(httpx.Response(200, json=SSO_PROVIDER_ROW))

    verified_sso_provider = api.client.organizations.sso_provider.verifications.create(
        organization_id="organization"
    )

    assert verified_sso_provider == SsoProvider.model_validate(SSO_PROVIDER_ROW)
    assert api.sent_methods_and_urls == [
        "POST https://api.hotcodepush.com/v1/organizations/organization/sso-provider/verifications"
    ]
    assert api.last_request.content == b""


def test_retries_the_verification_when_the_api_is_unavailable() -> None:
    api = StubApi(httpx.Response(503))

    with pytest.raises(HotCodePushError):
        api.client.organizations.sso_provider.verifications.create(organization_id="organization")

    assert len(api.requests) == 3
