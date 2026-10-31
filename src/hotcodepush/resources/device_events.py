from __future__ import annotations

from .._http import resolve_path
from .._types import NOT_GIVEN, NotGiven
from ..models import Count, ReleaseDeviceEvent
from ._base import BaseResource


class DeviceEventsResource(BaseResource):
    def count(
        self, *, app_id: str, device_id: str, release_id: str | NotGiven = NOT_GIVEN
    ) -> Count:
        """Counts the events of the device that match the filter."""
        return self._http_client.fetch_json(
            "GET",
            resolve_path(
                "/v1/apps/{appId}/devices/{deviceId}/events/count",
                appId=app_id,
                deviceId=device_id,
            ),
            Count,
            query={"releaseId": release_id},
        )

    def list(
        self,
        *,
        app_id: str,
        device_id: str,
        limit: int | NotGiven = NOT_GIVEN,
        offset: int | NotGiven = NOT_GIVEN,
        release_id: str | NotGiven = NOT_GIVEN,
    ) -> list[ReleaseDeviceEvent]:
        """Lists the events of the device across the releases of the app, newest first.

        `release_id` selects the events of one release.
        """
        return self._http_client.fetch_json(
            "GET",
            resolve_path(
                "/v1/apps/{appId}/devices/{deviceId}/events", appId=app_id, deviceId=device_id
            ),
            list[ReleaseDeviceEvent],
            query={"limit": limit, "offset": offset, "releaseId": release_id},
        )
