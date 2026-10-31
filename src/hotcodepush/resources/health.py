from __future__ import annotations

from ._base import BaseResource


class HealthResource(BaseResource):
    def get(self) -> None:
        """Checks that the API is up.

        Returns when the API answers its plain-text `ok`. Raises a `HotCodePushError` on
        `unavailable` or any other status outside 2xx.
        """
        self._http_client.fetch_status("GET", "/health")
