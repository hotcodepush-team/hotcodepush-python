from __future__ import annotations

from .._http import HttpClient, resolve_path
from .._types import NOT_GIVEN, NotGiven
from ..models import Usage
from ._base import BaseResource
from .usage_apps import UsageAppsResource


class UsageResource(BaseResource):
    def __init__(self, http_client: HttpClient) -> None:
        super().__init__(http_client)
        self.apps = UsageAppsResource(http_client)

    def get(self, *, month: str | NotGiven = NOT_GIVEN, organization_id: str) -> Usage:
        """Gets the usage of the organization in `month`, `YYYY-MM`, by default the current month.

        The API reads it from the stored months.
        """
        return self._http_client.fetch_json(
            "GET",
            resolve_path(
                "/v1/organizations/{organizationId}/usage", organizationId=organization_id
            ),
            Usage,
            query={"month": month},
        )
