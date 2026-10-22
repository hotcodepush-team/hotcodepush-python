from __future__ import annotations

from typing import Literal

from .._http import resolve_path
from .._types import NOT_GIVEN, NotGiven
from ._base import BaseResource


class ChannelQrResource(BaseResource):
    def get(
        self,
        *,
        app_id: str,
        channel_id: str,
        format: Literal["png", "svg"] | NotGiven = NOT_GIVEN,
    ) -> bytes:
        """The channel's deep link from the app's `channel_link_template` as a QR image, SVG
        unless `format` is `png`; `E_NOT_FOUND` while the template is unset.
        """
        return self._http_client.fetch_bytes(
            "GET",
            resolve_path(
                "/v1/apps/{appId}/channels/{channelId}/qr", appId=app_id, channelId=channel_id
            ),
            query={"format": format},
        )
