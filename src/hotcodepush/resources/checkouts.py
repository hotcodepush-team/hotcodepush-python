from __future__ import annotations

from .._http import resolve_path
from ..models import Checkout
from ._base import BaseResource


class CheckoutsResource(BaseResource):
    def create(self, *, organization_id: str) -> Checkout:
        """Enables billing on a free organization: the Polar checkout for pay-as-you-go, the
        caller's email pre-filled and editable on Polar's page; the subscription arrives once it
        is paid, names the organization, and starts at the $5 minimum spending cap, which the
        customer raises afterwards.

        Each call creates another checkout and the API keeps no `Idempotency-Key` for it, so the
        call is never retried.

        An API token answers `E_FORBIDDEN`; sign in with a session.
        """
        return self._http_client.fetch_json(
            "POST",
            resolve_path(
                "/v1/organizations/{organizationId}/checkouts", organizationId=organization_id
            ),
            Checkout,
        )
