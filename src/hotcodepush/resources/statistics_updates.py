from __future__ import annotations

from datetime import date

from .._http import resolve_path
from .._types import NOT_GIVEN, NotGiven
from ..models import UpdateStatistics
from ._base import BaseResource


class StatisticsUpdatesResource(BaseResource):
    def get(
        self,
        *,
        app_id: str,
        channel_id: str | NotGiven = NOT_GIVEN,
        period_since: date | NotGiven = NOT_GIVEN,
        period_until: date | NotGiven = NOT_GIVEN,
        release_id: str | NotGiven = NOT_GIVEN,
    ) -> UpdateStatistics:
        """Gets the update statistics from `period_since` to `period_until`, both inclusive.

        `channel_id` limits them to one channel. `release_id` limits the adoption curves to that
        release, whatever its age.
        """
        return self._http_client.fetch_json(
            "GET",
            resolve_path("/v1/apps/{appId}/statistics/updates", appId=app_id),
            UpdateStatistics,
            query={
                "channelId": channel_id,
                "periodSince": period_since,
                "periodUntil": period_until,
                "releaseId": release_id,
            },
        )
