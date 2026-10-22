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
        rollout_percentage: int | NotGiven = NOT_GIVEN,
    ) -> Audience:
        """The devices a release's conditions would reach in the channel before it exists; each
        condition repeats, and repeated conditions combine with AND.

        An `attribute` is `key=value`, a `device` a device id.
        """
        return self._http_client.fetch_json(
            "GET",
            resolve_path(
                "/v1/apps/{appId}/channels/{channelId}/audience",
                appId=app_id,
                channelId=channel_id,
            ),
            Audience,
            query={
                "attribute": attribute,
                "binary": binary,
                "device": device,
                "fingerprint": fingerprint,
                "os": os,
                "rolloutPercentage": rollout_percentage,
            },
        )
