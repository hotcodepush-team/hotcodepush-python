from __future__ import annotations

from datetime import datetime

from .._http import HttpClient, resolve_path
from .._types import NOT_GIVEN, NotGiven
from ..models import Channel, Count, FailureAction
from ._base import BaseResource
from .channel_qr import ChannelQrResource
from .channel_releases import ChannelReleasesResource


class ChannelsResource(BaseResource):
    def __init__(self, http_client: HttpClient) -> None:
        super().__init__(http_client)
        self.qr = ChannelQrResource(http_client)
        self.releases = ChannelReleasesResource(http_client)

    def count(self, *, app_id: str, query: str | NotGiven = NOT_GIVEN) -> Count:
        """The number of the app's channels under the list's filters."""
        return self._http_client.fetch_json(
            "GET",
            resolve_path("/v1/apps/{appId}/channels/count", appId=app_id),
            Count,
            query={"query": query},
        )

    def create(
        self,
        *,
        app_id: str,
        expires_at: datetime | None | NotGiven = NOT_GIVEN,
        failure_action: FailureAction | None | NotGiven = NOT_GIVEN,
        failure_minimum_update_count: int | None | NotGiven = NOT_GIVEN,
        failure_threshold_percent: int | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | NotGiven = NOT_GIVEN,
        is_discoverable: bool | NotGiven = NOT_GIVEN,
        is_protected: bool | NotGiven = NOT_GIVEN,
        name: str,
    ) -> Channel:
        """Creates a channel; the name is one to 64 letters, digits, hyphens or underscores and
        unique per app.
        """
        return self._http_client.fetch_creating_post(
            resolve_path("/v1/apps/{appId}/channels", appId=app_id),
            Channel,
            body={
                "expiresAt": expires_at,
                "failureAction": failure_action,
                "failureMinimumUpdateCount": failure_minimum_update_count,
                "failureThresholdPercent": failure_threshold_percent,
                "isDiscoverable": is_discoverable,
                "isProtected": is_protected,
                "name": name,
            },
            idempotency_key=idempotency_key,
        )

    def delete(self, *, app_id: str, channel_id: str) -> None:
        """Deletes a channel at once; the app's default channel is refused."""
        self._http_client.fetch_status(
            "DELETE",
            resolve_path(
                "/v1/apps/{appId}/channels/{channelId}", appId=app_id, channelId=channel_id
            ),
        )

    def delete_many(self, *, app_id: str, ids: list[str]) -> None:
        """Deletes the app's channels named by `ids`, one to 100; an id of another app is skipped.

        The app's default channel, or a protected channel when the caller is a Member, refuses
        the whole set.
        """
        self._http_client.fetch_status(
            "DELETE",
            resolve_path("/v1/apps/{appId}/channels", appId=app_id),
            query={"ids": ids},
        )

    def get(self, *, app_id: str, channel_id: str) -> Channel:
        """A channel; `apps.statistics.fleet.get` with its `channel_id` counts its devices."""
        return self._http_client.fetch_json(
            "GET",
            resolve_path(
                "/v1/apps/{appId}/channels/{channelId}", appId=app_id, channelId=channel_id
            ),
            Channel,
        )

    def list(
        self,
        *,
        app_id: str,
        limit: int | NotGiven = NOT_GIVEN,
        offset: int | NotGiven = NOT_GIVEN,
        query: str | NotGiven = NOT_GIVEN,
    ) -> list[Channel]:
        """The app's channels, newest first; `query` selects those whose name contains it."""
        return self._http_client.fetch_json(
            "GET",
            resolve_path("/v1/apps/{appId}/channels", appId=app_id),
            list[Channel],
            query={"limit": limit, "offset": offset, "query": query},
        )

    def pause(self, *, app_id: str, channel_id: str) -> Channel:
        """Pauses a channel: it serves nothing new, and devices keep what they have.

        Pausing a paused channel answers it unchanged, so the call is retried.
        """
        return self._http_client.fetch_json(
            "POST",
            resolve_path(
                "/v1/apps/{appId}/channels/{channelId}/pause", appId=app_id, channelId=channel_id
            ),
            Channel,
            is_retryable=True,
        )

    def resume(self, *, app_id: str, channel_id: str) -> Channel:
        """Resumes a paused channel.

        Resuming a running channel answers it unchanged, so the call is retried.
        """
        return self._http_client.fetch_json(
            "POST",
            resolve_path(
                "/v1/apps/{appId}/channels/{channelId}/resume", appId=app_id, channelId=channel_id
            ),
            Channel,
            is_retryable=True,
        )

    def update(
        self,
        *,
        app_id: str,
        channel_id: str,
        expires_at: datetime | None | NotGiven = NOT_GIVEN,
        failure_action: FailureAction | None | NotGiven = NOT_GIVEN,
        failure_minimum_update_count: int | None | NotGiven = NOT_GIVEN,
        failure_threshold_percent: int | None | NotGiven = NOT_GIVEN,
        is_discoverable: bool | NotGiven = NOT_GIVEN,
        is_protected: bool | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
    ) -> Channel:
        """Edits the name, the protected and discoverable flags, the expiry and the auto-pause
        policy; `None` clears a nullable one.
        """
        return self._http_client.fetch_json(
            "PATCH",
            resolve_path(
                "/v1/apps/{appId}/channels/{channelId}", appId=app_id, channelId=channel_id
            ),
            Channel,
            body={
                "expiresAt": expires_at,
                "failureAction": failure_action,
                "failureMinimumUpdateCount": failure_minimum_update_count,
                "failureThresholdPercent": failure_threshold_percent,
                "isDiscoverable": is_discoverable,
                "isProtected": is_protected,
                "name": name,
            },
        )
