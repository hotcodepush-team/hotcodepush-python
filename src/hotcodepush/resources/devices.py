from __future__ import annotations

from datetime import datetime

from .._http import HttpClient, resolve_path
from .._types import NOT_GIVEN, NotGiven
from ..models import Count, Device, DeviceRelation, Platform
from ._base import BaseResource
from .device_events import DeviceEventsResource


class DevicesResource(BaseResource):
    def __init__(self, http_client: HttpClient) -> None:
        super().__init__(http_client)
        self.events = DeviceEventsResource(http_client)

    def count(
        self,
        *,
        app_id: str,
        attribute: str | NotGiven = NOT_GIVEN,
        binary_build: str | NotGiven = NOT_GIVEN,
        binary_version: str | NotGiven = NOT_GIVEN,
        channel_id: str | NotGiven = NOT_GIVEN,
        fingerprint: str | NotGiven = NOT_GIVEN,
        last_seen_since: datetime | NotGiven = NOT_GIVEN,
        last_seen_until: datetime | NotGiven = NOT_GIVEN,
        platform: Platform | NotGiven = NOT_GIVEN,
        sdk_version: str | NotGiven = NOT_GIVEN,
    ) -> Count:
        """Counts the devices of the app that match the filters."""
        return self._http_client.fetch_json(
            "GET",
            resolve_path("/v1/apps/{appId}/devices/count", appId=app_id),
            Count,
            query={
                "attribute": attribute,
                "binaryBuild": binary_build,
                "binaryVersion": binary_version,
                "channelId": channel_id,
                "fingerprint": fingerprint,
                "lastSeenSince": last_seen_since,
                "lastSeenUntil": last_seen_until,
                "platform": platform,
                "sdkVersion": sdk_version,
            },
        )

    def delete(self, *, app_id: str, device_id: str) -> None:
        """Deletes the registry row of a device, for an erasure request."""
        self._http_client.fetch_status(
            "DELETE",
            resolve_path("/v1/apps/{appId}/devices/{deviceId}", appId=app_id, deviceId=device_id),
        )

    def delete_many(self, *, app_id: str, ids: list[str]) -> None:
        """Deletes the devices of the app named by `ids`, 1 to 100.

        An id of another app is skipped.
        """
        self._http_client.fetch_status(
            "DELETE",
            resolve_path("/v1/apps/{appId}/devices", appId=app_id),
            query={"ids": ids},
        )

    def get(
        self,
        *,
        app_id: str,
        device_id: str,
        relations: list[DeviceRelation] | NotGiven = NOT_GIVEN,
    ) -> Device:
        return self._http_client.fetch_json(
            "GET",
            resolve_path("/v1/apps/{appId}/devices/{deviceId}", appId=app_id, deviceId=device_id),
            Device,
            query={"relations": relations},
        )

    def list(
        self,
        *,
        app_id: str,
        attribute: str | NotGiven = NOT_GIVEN,
        binary_build: str | NotGiven = NOT_GIVEN,
        binary_version: str | NotGiven = NOT_GIVEN,
        channel_id: str | NotGiven = NOT_GIVEN,
        fingerprint: str | NotGiven = NOT_GIVEN,
        last_seen_since: datetime | NotGiven = NOT_GIVEN,
        last_seen_until: datetime | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        offset: int | NotGiven = NOT_GIVEN,
        platform: Platform | NotGiven = NOT_GIVEN,
        relations: list[DeviceRelation] | NotGiven = NOT_GIVEN,
        sdk_version: str | NotGiven = NOT_GIVEN,
    ) -> list[Device]:
        """Lists the devices of the app, newest report first.

        `attribute` takes one `key=value`.
        """
        return self._http_client.fetch_json(
            "GET",
            resolve_path("/v1/apps/{appId}/devices", appId=app_id),
            list[Device],
            query={
                "attribute": attribute,
                "binaryBuild": binary_build,
                "binaryVersion": binary_version,
                "channelId": channel_id,
                "fingerprint": fingerprint,
                "lastSeenSince": last_seen_since,
                "lastSeenUntil": last_seen_until,
                "limit": limit,
                "offset": offset,
                "platform": platform,
                "relations": relations,
                "sdkVersion": sdk_version,
            },
        )
