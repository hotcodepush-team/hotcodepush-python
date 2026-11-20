from __future__ import annotations

from .._http import resolve_path
from .._types import NOT_GIVEN, NotGiven
from ..models import Audience
from ._base import BaseResource


class ChannelAudienceResource(BaseResource):
    def get(
        self,
        *,
        app_id: str,
        attribute: list[str] | NotGiven = NOT_GIVEN,
        binary: list[str] | NotGiven = NOT_GIVEN,
        channel_id: str,
        device: list[str] | NotGiven = NOT_GIVEN,
        fingerprint: list[str] | NotGiven = NOT_GIVEN,
        os: list[str] | NotGiven = NOT_GIVEN,
        progression_rollout_percent: list[int] | NotGiven = NOT_GIVEN,
        progression_step_minimum_update_count: int | NotGiven = NOT_GIVEN,
        rollout_percent: int | NotGiven = NOT_GIVEN,
    ) -> Audience:
        """Gets the devices that a release with these conditions would reach in the channel.

        Use it before creating the release. Each condition can repeat, and all conditions must
        match. An `attribute` is `key=value`, and a `device` is a device id.

        `progression_rollout_percent` is valid only beside `progression_step_minimum_update_count`.
        Together they add the warning `progression_step_too_small` when a step adds fewer devices
        than the applied updates it waits for.
        """
        return self._http_client.fetch_json(
            method="GET",
            path=resolve_path(
                "/v1/apps/{appId}/channels/{channelId}/audience",
                appId=app_id,
                channelId=channel_id,
            ),
            query={
                "attribute": attribute,
                "binary": binary,
                "device": device,
                "fingerprint": fingerprint,
                "os": os,
                "progressionRolloutPercent": progression_rollout_percent,
                "progressionStepMinimumUpdateCount": progression_step_minimum_update_count,
                "rolloutPercent": rollout_percent,
            },
            response_type=Audience,
        )
