from __future__ import annotations

from .._http import resolve_path
from ._base import BaseResource


class UserSessionsResource(BaseResource):
    def delete_many(self, *, ids: list[str], user_id: str) -> None:
        """Ends your sessions named by `ids`, 1 to 100, the current one included.

        An id that is not yours is skipped.

        An API token answers `forbidden`; sign in with a session.
        """
        self._http_client.fetch_status(
            "DELETE",
            resolve_path("/v1/users/{userId}/sessions", userId=user_id),
            query={"ids": ids},
        )
