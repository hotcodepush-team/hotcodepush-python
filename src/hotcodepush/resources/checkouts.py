from __future__ import annotations

from .._http import resolve_path
from ..models import Checkout
from ._base import BaseResource


class CheckoutsResource(BaseResource):
    def create(self, *, organization_id: str) -> Checkout:
        """Creates a Polar checkout that enables pay-as-you-go billing on a free organization.

        Your email is pre-filled and can be changed on the Polar page. Once paid, the subscription
        names the organization and starts at the $5 minimum spending cap, which you can raise later.

        Never retried, since each call creates another checkout and the API keeps no
        `Idempotency-Key` for it.

        An API token answers `forbidden`; sign in with a session.
        """
        return self._http_client.fetch_json(
            "POST",
            resolve_path(
                "/v1/organizations/{organizationId}/checkouts", organizationId=organization_id
            ),
            Checkout,
        )
