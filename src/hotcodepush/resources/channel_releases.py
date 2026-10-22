from __future__ import annotations

import builtins

from .._http import resolve_path
from .._types import NOT_GIVEN, NotGiven
from ..models import (
    Count,
    FailureAction,
    Release,
    ReleaseCondition,
    ReleaseProgression,
    ReleaseRelation,
)
from ._base import BaseResource


class ChannelReleasesResource(BaseResource):
    def count(self, *, app_id: str, channel_id: str, number: int | NotGiven = NOT_GIVEN) -> Count:
        """The number of releases in the channel's log under the list's filter."""
        return self._http_client.fetch_json(
            "GET",
            resolve_path(
                "/v1/apps/{appId}/channels/{channelId}/releases/count",
                appId=app_id,
                channelId=channel_id,
            ),
            Count,
            query={"number": number},
        )

    def create(
        self,
        *,
        app_id: str,
        bundle_id: str | NotGiven = NOT_GIVEN,
        channel_id: str,
        conditions: list[ReleaseCondition] | NotGiven = NOT_GIVEN,
        failure_action: FailureAction | None | NotGiven = NOT_GIVEN,
        failure_minimum_update_count: int | None | NotGiven = NOT_GIVEN,
        failure_threshold_percent: int | None | NotGiven = NOT_GIVEN,
        from_channel_id: str | NotGiven = NOT_GIVEN,
        idempotency_key: str | NotGiven = NOT_GIVEN,
        is_mandatory: bool | NotGiven = NOT_GIVEN,
        notes: str | None | NotGiven = NOT_GIVEN,
        progression: ReleaseProgression | None | NotGiven = NOT_GIVEN,
        rollout_percentage: int | NotGiven = NOT_GIVEN,
    ) -> Release:
        """Releases a ready bundle, `bundle_id`, or what another channel serves,
        `from_channel_id`, in the channel, numbered next in the channel.
        """
        return self._http_client.fetch_creating_post(
            resolve_path(
                "/v1/apps/{appId}/channels/{channelId}/releases",
                appId=app_id,
                channelId=channel_id,
            ),
            Release,
            body={
                "bundleId": bundle_id,
                "conditions": conditions,
                "failureAction": failure_action,
                "failureMinimumUpdateCount": failure_minimum_update_count,
                "failureThresholdPercent": failure_threshold_percent,
                "fromChannelId": from_channel_id,
                "isMandatory": is_mandatory,
                "notes": notes,
                "progression": progression,
                "rolloutPercentage": rollout_percentage,
            },
            idempotency_key=idempotency_key,
        )

    def list(
        self,
        *,
        app_id: str,
        channel_id: str,
        limit: int | NotGiven = NOT_GIVEN,
        number: int | NotGiven = NOT_GIVEN,
        offset: int | NotGiven = NOT_GIVEN,
        relations: list[ReleaseRelation] | NotGiven = NOT_GIVEN,
    ) -> list[Release]:
        """The channel's release log, newest first, or the one release `number` names."""
        return self._http_client.fetch_json(
            "GET",
            resolve_path(
                "/v1/apps/{appId}/channels/{channelId}/releases",
                appId=app_id,
                channelId=channel_id,
            ),
            list[Release],
            query={"limit": limit, "number": number, "offset": offset, "relations": relations},
        )

    def revoke(
        self,
        *,
        app_id: str,
        channel_id: str,
        from_number: int | NotGiven = NOT_GIVEN,
        release_ids: builtins.list[str] | NotGiven = NOT_GIVEN,
    ) -> builtins.list[Release]:
        """Revokes several releases of the channel at once, the ones of `release_ids` or every
        one numbered at or above `from_number`.

        A release already revoked is a no-op, so the call is retried.
        """
        return self._http_client.fetch_json(
            "POST",
            resolve_path(
                "/v1/apps/{appId}/channels/{channelId}/releases/revoke",
                appId=app_id,
                channelId=channel_id,
            ),
            builtins.list[Release],
            body={"fromNumber": from_number, "releaseIds": release_ids},
            is_retryable=True,
        )
