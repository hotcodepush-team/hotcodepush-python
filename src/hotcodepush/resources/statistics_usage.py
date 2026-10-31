from __future__ import annotations

from datetime import date

from .._http import resolve_path
from .._types import NOT_GIVEN, NotGiven
from ..models import UsageStatistics
from ._base import BaseResource


class StatisticsUsageResource(BaseResource):
    def get(
        self,
        *,
        app_id: str,
        period_since: date | NotGiven = NOT_GIVEN,
        period_until: date | NotGiven = NOT_GIVEN,
    ) -> UsageStatistics:
        """Gets the usage statistics from `period_since` to `period_until`, both inclusive."""
        return self._http_client.fetch_json(
            "GET",
            resolve_path("/v1/apps/{appId}/statistics/usage", appId=app_id),
            UsageStatistics,
            query={"periodSince": period_since, "periodUntil": period_until},
        )
