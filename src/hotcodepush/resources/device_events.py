from __future__ import annotations

from .._http import resolve_path
from .._types import NOT_GIVEN, NotGiven
from ..models import Count, ReleaseDeviceEvent
from ._base import BaseResource


class DeviceEventsResource(BaseResource):
    def count(
        self, *, app_id: str, device_id: str, release_id: str | NotGiven = NOT_GIVEN
    ) -> Count:
        """The number of the device's events under the list's filter."""
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
        """The device's events across the app's releases, newest first, filtered by
        `release_id`.
        """
        return self._http_client.fetch_json(
            "GET",
            resolve_path(
                "/v1/apps/{appId}/devices/{deviceId}/events", appId=app_id, deviceId=device_id
            ),
            list[ReleaseDeviceEvent],
            query={"limit": limit, "offset": offset, "releaseId": release_id},
        )
