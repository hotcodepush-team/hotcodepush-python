from __future__ import annotations

from .._http import resolve_path
from ..models import SsoProvider
from ._base import BaseResource


class SsoProviderVerificationsResource(BaseResource):
    def create(self, *, organization_id: str) -> SsoProvider:
        """Verifies the domain of the SSO provider.

        The API looks up the TXT record of the domain. If the record carries the
        `domain_verification_token`, the API sets `domain_verified`. Either way, it answers the
        provider. It answers `dns_lookup_failed` when it cannot reach a DNS resolver.

        Retried, since a verified provider answers unchanged without a lookup.

        An API token answers `forbidden`; sign in with a session.
        """
        return self._http_client.fetch_json(
            "POST",
            resolve_path(
                "/v1/organizations/{organizationId}/sso-provider/verifications",
                organizationId=organization_id,
            ),
            SsoProvider,
            is_retryable=True,
        )
