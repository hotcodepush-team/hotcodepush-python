from __future__ import annotations

from .._http import resolve_path
from ..models import CustomerPortalSession
from ._base import BaseResource


class CustomerPortalSessionsResource(BaseResource):
    def create(self, *, organization_id: str) -> CustomerPortalSession:
        """Creates a session of the Polar customer portal.

        The portal shows the invoices and payment method of the organization. An organization that
        never subscribed has none.

        Never retried, since each call creates another session and the API keeps no
        `Idempotency-Key` for it.

        An API token answers `forbidden`; sign in with a session.
        """
        return self._http_client.fetch_json(
            "POST",
            resolve_path(
                "/v1/organizations/{organizationId}/customer-portal-sessions",
                organizationId=organization_id,
            ),
            response_type=CustomerPortalSession,
        )
