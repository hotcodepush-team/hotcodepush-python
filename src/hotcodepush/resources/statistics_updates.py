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
        """The update statistics of the period, `period_since` to `period_until` inclusive, of
        one channel when `channel_id` names it; `release_id` narrows the adoption curves to that
        one release, whatever its age.
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
