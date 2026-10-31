from __future__ import annotations

from .._http import HttpClient, resolve_path
from .._types import NOT_GIVEN, NotGiven
from ..models import OidcConfig, SamlConfig, SsoProvider
from ._base import BaseResource
from .sso_provider_verifications import SsoProviderVerificationsResource


class SsoProviderResource(BaseResource):
    """The one SSO provider of the organization."""

    def __init__(self, http_client: HttpClient) -> None:
        super().__init__(http_client)
        self.verifications = SsoProviderVerificationsResource(http_client)

    def delete(self, *, organization_id: str) -> None:
        """Removes the SSO provider.

        Its members can sign in with a password again, and the domain is forgotten.

        An API token answers `forbidden`; sign in with a session.
        """
        self._http_client.fetch_status(
            "DELETE",
            resolve_path(
                "/v1/organizations/{organizationId}/sso-provider", organizationId=organization_id
            ),
        )

    def get(self, *, organization_id: str) -> SsoProvider:
        """Gets the SSO provider.

        An API token answers `forbidden`; sign in with a session.
        """
        return self._http_client.fetch_json(
            "GET",
            resolve_path(
                "/v1/organizations/{organizationId}/sso-provider", organizationId=organization_id
            ),
            SsoProvider,
        )

    def set(
        self,
        *,
        domain: str,
        oidc: OidcConfig | NotGiven = NOT_GIVEN,
        organization_id: str,
        saml: SamlConfig | NotGiven = NOT_GIVEN,
    ) -> SsoProvider:
        """Sets the SSO provider and its domain, replacing the one before.

        Pass exactly one of `oidc` and `saml`. A new or changed domain starts unverified, with a new
        token for its TXT record.

        An API token answers `forbidden`; sign in with a session.
        """
        return self._http_client.fetch_json(
            "PUT",
            resolve_path(
                "/v1/organizations/{organizationId}/sso-provider", organizationId=organization_id
            ),
            SsoProvider,
            body={"domain": domain, "oidc": oidc, "saml": saml},
        )
