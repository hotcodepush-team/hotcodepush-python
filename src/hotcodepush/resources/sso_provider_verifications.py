from __future__ import annotations

from .._http import resolve_path
from ..models import SsoProvider
from ._base import BaseResource


class SsoProviderVerificationsResource(BaseResource):
    def create(self, *, organization_id: str) -> SsoProvider:
        """Looks up the domain's TXT record for the provider's `domain_verification_token` and
        sets `domain_verified` when the record carries it; the answer is the provider, verified or
        still waiting for the record, and a resolver that cannot be asked answers
        `E_DNS_LOOKUP_FAILED`.

        A verified provider answers unchanged without a lookup, so the call is retried.

        An API token answers `E_FORBIDDEN`; sign in with a session.
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
