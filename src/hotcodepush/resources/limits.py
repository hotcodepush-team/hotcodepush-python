from __future__ import annotations

from .._http import resolve_path
from ..models import Limit
from ._base import BaseResource


class LimitsResource(BaseResource):
    def get(self, *, organization_id: str) -> dict[str, Limit]:
        """Gets every limit in effect for the organization, keyed by name.

        An API token answers `forbidden`; sign in with a session.
        """
        return self._http_client.fetch_json(
            "GET",
            resolve_path(
                "/v1/organizations/{organizationId}/limits", organizationId=organization_id
            ),
            dict[str, Limit],
        )
