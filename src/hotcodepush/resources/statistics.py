from __future__ import annotations

from .._http import HttpClient
from ._base import BaseResource
from .statistics_fleet import StatisticsFleetResource
from .statistics_updates import StatisticsUpdatesResource
from .statistics_usage import StatisticsUsageResource


class StatisticsResource(BaseResource):
    def __init__(self, http_client: HttpClient) -> None:
        super().__init__(http_client)
        self.fleet = StatisticsFleetResource(http_client)
        self.updates = StatisticsUpdatesResource(http_client)
        self.usage = StatisticsUsageResource(http_client)
