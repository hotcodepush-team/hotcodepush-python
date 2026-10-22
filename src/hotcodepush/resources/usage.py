from __future__ import annotations

from .._http import resolve_path
from .._types import NOT_GIVEN, NotGiven
from ..models import AppUsageMonth, AppUsageMonthRelation, Count, Usage
from ._base import BaseResource


class UsageResource(BaseResource):
    def count_apps(self, *, month: str | NotGiven = NOT_GIVEN, organization_id: str) -> Count:
        """The number of apps with usage in `month`, `YYYY-MM`, which `list_apps` pages through."""
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
        """Every app's usage in `month`, `YYYY-MM`, as `text/csv` with the app's name, read whole."""
        return self._http_client.fetch_bytes(
            "GET",
            resolve_path(
                "/v1/organizations/{organizationId}/usage/apps", organizationId=organization_id
            ),
            query={"format": "csv", "month": month},
        )

    def get(self, *, month: str | NotGiven = NOT_GIVEN, organization_id: str) -> Usage:
        """The organization's usage in `month`, `YYYY-MM`, the current one by default, read from
        the stored months.
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
        """The usage of each live app in `month`, `YYYY-MM`, the most monthly active devices
        first; `relations=["app"]` embeds the app's id and name.
        """
        return self._http_client.fetch_json(
            "GET",
            resolve_path(
                "/v1/organizations/{organizationId}/usage/apps", organizationId=organization_id
            ),
            list[AppUsageMonth],
            query={"limit": limit, "month": month, "offset": offset, "relations": relations},
        )
