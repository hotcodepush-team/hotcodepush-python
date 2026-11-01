from __future__ import annotations

from .._http import resolve_path
from .._types import NOT_GIVEN, NotGiven
from ..models import FailureAction, Release, ReleaseCondition, ReleaseProgression
from ._base import BaseResource


class ChannelReleasesResource(BaseResource):
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
        rollout_percent: int | NotGiven = NOT_GIVEN,
    ) -> Release:
        """Creates a release in the channel with the next number.

        It releases either a ready bundle, `bundle_id`, or what another channel serves,
        `from_channel_id`.
        """
        return self._http_client.fetch_creating_post(
            resolve_path(
                "/v1/apps/{appId}/channels/{channelId}/releases",
                appId=app_id,
                channelId=channel_id,
            ),
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
                "rolloutPercent": rollout_percent,
            },
            idempotency_key=idempotency_key,
            response_type=Release,
        )

    def revoke(
        self,
        *,
        app_id: str,
        channel_id: str,
        from_number: int | NotGiven = NOT_GIVEN,
        release_ids: list[str] | NotGiven = NOT_GIVEN,
    ) -> list[Release]:
        """Revokes several releases of the channel at once.

        It revokes the releases in `release_ids`, or every release numbered `from_number` or above.
        Retried, since revoking a revoked release changes nothing.
        """
        return self._http_client.fetch_json(
            "POST",
            resolve_path(
                "/v1/apps/{appId}/channels/{channelId}/releases/revoke",
                appId=app_id,
                channelId=channel_id,
            ),
            body={"fromNumber": from_number, "releaseIds": release_ids},
            is_retryable=True,
            response_type=list[Release],
        )
