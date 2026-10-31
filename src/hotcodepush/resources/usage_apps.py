from __future__ import annotations

from .._http import resolve_path
from .._types import NOT_GIVEN, NotGiven
from ..models import AppUsageMonth, AppUsageMonthRelation, Count
from ._base import BaseResource


class UsageAppsResource(BaseResource):
    def count(self, *, month: str | NotGiven = NOT_GIVEN, organization_id: str) -> Count:
        """Counts the apps with usage in `month`, `YYYY-MM`.

        `list` pages through them.
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

    def download_csv(self, *, month: str | NotGiven = NOT_GIVEN, organization_id: str) -> bytes:
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

    def list(
        self,
        *,
        limit: int | NotGiven = NOT_GIVEN,
        month: str | NotGiven = NOT_GIVEN,
        offset: int | NotGiven = NOT_GIVEN,
        organization_id: str,
        relations: list[AppUsageMonthRelation] | NotGiven = NOT_GIVEN,
    ) -> list[AppUsageMonth]:
        """Lists the usage of each live app in `month`, `YYYY-MM`.

        The app with the most monthly active devices comes first. `relations=["app"]` embeds the
        id and name of each app.
        """
        return self._http_client.fetch_json(
            "GET",
            resolve_path(
                "/v1/organizations/{organizationId}/usage/apps", organizationId=organization_id
            ),
            list[AppUsageMonth],
            query={"limit": limit, "month": month, "offset": offset, "relations": relations},
        )
