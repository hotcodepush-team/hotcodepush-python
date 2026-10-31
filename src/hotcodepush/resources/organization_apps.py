from __future__ import annotations

from .._http import resolve_path
from .._types import NOT_GIVEN, NotGiven
from ..models import App, Count, Framework
from ._base import BaseResource


class OrganizationAppsResource(BaseResource):
    def count(self, *, organization_id: str, query: str | NotGiven = NOT_GIVEN) -> Count:
        """Counts the apps of the organization that match the filters."""
        return self._http_client.fetch_json(
            "GET",
            resolve_path(
                "/v1/organizations/{organizationId}/apps/count", organizationId=organization_id
            ),
            Count,
            query={"query": query},
        )

    def create(
        self,
        *,
        framework: Framework,
        idempotency_key: str | NotGiven = NOT_GIVEN,
        name: str,
        organization_id: str,
    ) -> App:
        """Creates an app with the default channel `production`."""
        return self._http_client.fetch_creating_post(
            resolve_path("/v1/organizations/{organizationId}/apps", organizationId=organization_id),
            App,
            body={"framework": framework, "name": name},
            idempotency_key=idempotency_key,
        )

    def list(
        self,
        *,
        limit: int | NotGiven = NOT_GIVEN,
        offset: int | NotGiven = NOT_GIVEN,
        organization_id: str,
        query: str | NotGiven = NOT_GIVEN,
    ) -> list[App]:
        """Lists the apps of the organization, newest first.

        `query` selects the apps whose name contains it.
        """
        return self._http_client.fetch_json(
            "GET",
            resolve_path("/v1/organizations/{organizationId}/apps", organizationId=organization_id),
            list[App],
            query={"limit": limit, "offset": offset, "query": query},
        )
