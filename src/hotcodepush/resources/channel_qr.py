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
        """Gets the deep link of the channel as a QR image, SVG unless `format` is `png`.

        The link comes from the app's `channel_link_template`. Answers `not_found` while the
        template is unset.
        """
        return self._http_client.fetch_bytes(
            "GET",
            resolve_path(
                "/v1/apps/{appId}/channels/{channelId}/qr", appId=app_id, channelId=channel_id
            ),
            query={"format": format},
        )
