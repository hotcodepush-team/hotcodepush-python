from __future__ import annotations

from .._http import resolve_path
from .._types import NOT_GIVEN, NotGiven
from ..models import FleetStatistics
from ._base import BaseResource


class StatisticsFleetResource(BaseResource):
    def get(self, *, app_id: str, channel_id: str | NotGiven = NOT_GIVEN) -> FleetStatistics:
        """Gets a snapshot of the device fleet from the registry.

        `channel_id` limits it to one channel.
        """
        return self._http_client.fetch_json(
            "GET",
            resolve_path("/v1/apps/{appId}/statistics/fleet", appId=app_id),
            query={"channelId": channel_id},
            response_type=FleetStatistics,
        )
