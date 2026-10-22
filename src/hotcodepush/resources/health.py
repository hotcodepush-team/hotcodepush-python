from __future__ import annotations

from ._base import BaseResource


class HealthResource(BaseResource):
    def get(self) -> None:
        """Returns when the API answers its plain-text `ok`; `unavailable`, or any other status
        outside 2xx, raises a `HotCodePushError`.
        """
        self._http_client.fetch_status("GET", "/health")
