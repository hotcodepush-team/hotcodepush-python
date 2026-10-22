from __future__ import annotations

from .._http import resolve_path
from .._types import NOT_GIVEN, NotGiven
from ..models import FleetStatistics
from ._base import BaseResource


class StatisticsFleetResource(BaseResource):
    def get(self, *, app_id: str, channel_id: str | NotGiven = NOT_GIVEN) -> FleetStatistics:
        """The registry's snapshot of the fleet, of one channel when `channel_id` names it."""
        return self._http_client.fetch_json(
            "GET",
            resolve_path("/v1/apps/{appId}/statistics/fleet", appId=app_id),
            FleetStatistics,
            query={"channelId": channel_id},
        )
