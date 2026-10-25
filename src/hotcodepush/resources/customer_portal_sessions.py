from __future__ import annotations

from .._http import resolve_path
from ..models import CustomerPortalSession
from ._base import BaseResource


class CustomerPortalSessionsResource(BaseResource):
    def create(self, *, organization_id: str) -> CustomerPortalSession:
        """A session of Polar's customer portal for the organization's invoices and payment
        method; an organization that never subscribed has none.

        Each call creates another session and the API keeps no `Idempotency-Key` for it, so the
        call is never retried.

        An API token answers `forbidden`; sign in with a session.
        """
        return self._http_client.fetch_json(
            "POST",
            resolve_path(
                "/v1/organizations/{organizationId}/customer-portal-sessions",
                organizationId=organization_id,
            ),
            CustomerPortalSession,
        )
