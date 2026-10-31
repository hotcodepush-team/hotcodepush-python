from __future__ import annotations

from .._http import resolve_path
from .._types import NOT_GIVEN, NotGiven
from ..models import AppUsageMonth, AppUsageMonthRelation, Count, Usage
from ._base import BaseResource


class UsageResource(BaseResource):
    def count_apps(self, *, month: str | NotGiven = NOT_GIVEN, organization_id: str) -> Count:
        """Counts the apps with usage in `month`, `YYYY-MM`.

        `list_apps` pages through them.
        """
        return self._http_client.fetch_json(
            "GET",
            resolve_path(
                "/v1/organizations/{organizationId}/usage/apps/count",
                organizationId=organization_id,
            ),
            Count,
            query={"month": month},
        )

    def download_apps_csv(
        self, *, month: str | NotGiven = NOT_GIVEN, organization_id: str
    ) -> bytes:
        """Downloads the usage of every app in `month`, `YYYY-MM`, as `text/csv`.

        The CSV includes the app names.
        """
        return self._http_client.fetch_bytes(
            "GET",
            resolve_path(
                "/v1/organizations/{organizationId}/usage/apps", organizationId=organization_id
            ),
            query={"format": "csv", "month": month},
        )

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

    def list_apps(
        self,
        *,
        limit: int | NotGiven = NOT_GIVEN,
        month: str | NotGiven = NOT_GIVEN,
        offset: int | NotGiven = NOT_GIVEN,
        organization_id: str,
        relations: list[AppUsageMonthRelation] | NotGiven = NOT_GIVEN,
    ) -> list[AppUsageMonth]:
        """Lists the usage of each live app in `month`, `YYYY-MM`.

        The app with the most monthly active devices comes first. `relations=["app"]` embeds the id and name of each app.
        """
        return self._http_client.fetch_json(
            "GET",
            resolve_path(
                "/v1/organizations/{organizationId}/usage/apps", organizationId=organization_id
            ),
            list[AppUsageMonth],
            query={"limit": limit, "month": month, "offset": offset, "relations": relations},
        )
