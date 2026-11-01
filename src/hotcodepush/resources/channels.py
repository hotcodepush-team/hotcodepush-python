from __future__ import annotations

from datetime import datetime

from .._http import HttpClient, resolve_path
from .._types import NOT_GIVEN, NotGiven
from ..models import Channel, Count, FailureAction
from ._base import BaseResource
from .channel_audience import ChannelAudienceResource
from .channel_qr_code import ChannelQrCodeResource
from .channel_releases import ChannelReleasesResource
from .rollbacks import RollbacksResource


class ChannelsResource(BaseResource):
    def __init__(self, http_client: HttpClient) -> None:
        super().__init__(http_client)
        self.audience = ChannelAudienceResource(http_client)
        self.qr_code = ChannelQrCodeResource(http_client)
        self.releases = ChannelReleasesResource(http_client)
        self.rollbacks = RollbacksResource(http_client)

    def count(self, *, app_id: str, query: str | NotGiven = NOT_GIVEN) -> Count:
        """Counts the channels of the app that match the filters."""
        return self._http_client.fetch_json(
            "GET",
            resolve_path("/v1/apps/{appId}/channels/count", appId=app_id),
            query={"query": query},
            response_type=Count,
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
        """Creates a channel.

        The name has 1 to 64 letters, digits, hyphens or underscores, and is unique in the app.
        """
        return self._http_client.fetch_creating_post(
            resolve_path("/v1/apps/{appId}/channels", appId=app_id),
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
            response_type=Channel,
        )

    def delete(self, *, app_id: str, channel_id: str) -> None:
        """Deletes a channel at once. The default channel of the app is refused."""
        self._http_client.fetch_status(
            "DELETE",
            resolve_path(
                "/v1/apps/{appId}/channels/{channelId}", appId=app_id, channelId=channel_id
            ),
        )

    def delete_many(self, *, app_id: str, ids: list[str]) -> None:
        """Deletes the channels of the app named by `ids`, 1 to 100.

        An id of another app is skipped. The whole request is refused if it names the default
        channel, or a protected channel while the caller is a Member.
        """
        self._http_client.fetch_status(
            "DELETE",
            resolve_path("/v1/apps/{appId}/channels", appId=app_id),
            query={"ids": ids},
        )

    def get(self, *, app_id: str, channel_id: str) -> Channel:
        """Gets a channel.

        To count its devices, call `apps.statistics.fleet.get` with its `channel_id`.
        """
        return self._http_client.fetch_json(
            "GET",
            resolve_path(
                "/v1/apps/{appId}/channels/{channelId}", appId=app_id, channelId=channel_id
            ),
            response_type=Channel,
        )

    def list(
        self,
        *,
        app_id: str,
        limit: int | NotGiven = NOT_GIVEN,
        offset: int | NotGiven = NOT_GIVEN,
        query: str | NotGiven = NOT_GIVEN,
    ) -> list[Channel]:
        """Lists the channels of the app, newest first.

        `query` selects the channels whose name contains it.
        """
        return self._http_client.fetch_json(
            "GET",
            resolve_path("/v1/apps/{appId}/channels", appId=app_id),
            query={"limit": limit, "offset": offset, "query": query},
            response_type=list[Channel],
        )

    def pause(self, *, app_id: str, channel_id: str) -> Channel:
        """Pauses a channel. It serves nothing new, and devices keep what they have.

        Retried, since pausing a paused channel answers it unchanged.
        """
        return self._http_client.fetch_json(
            "POST",
            resolve_path(
                "/v1/apps/{appId}/channels/{channelId}/pause", appId=app_id, channelId=channel_id
            ),
            is_retryable=True,
            response_type=Channel,
        )

    def resume(self, *, app_id: str, channel_id: str) -> Channel:
        """Resumes a paused channel.

        Retried, since resuming a running channel answers it unchanged.
        """
        return self._http_client.fetch_json(
            "POST",
            resolve_path(
                "/v1/apps/{appId}/channels/{channelId}/resume", appId=app_id, channelId=channel_id
            ),
            is_retryable=True,
            response_type=Channel,
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
        """Updates the name, flags, expiry or auto-pause policy of a channel.

        The flags are `is_protected` and `is_discoverable`. `None` clears a nullable field.
        """
        return self._http_client.fetch_json(
            "PATCH",
            resolve_path(
                "/v1/apps/{appId}/channels/{channelId}", appId=app_id, channelId=channel_id
            ),
            body={
                "expiresAt": expires_at,
                "failureAction": failure_action,
                "failureMinimumUpdateCount": failure_minimum_update_count,
                "failureThresholdPercent": failure_threshold_percent,
                "isDiscoverable": is_discoverable,
                "isProtected": is_protected,
                "name": name,
            },
            response_type=Channel,
        )
