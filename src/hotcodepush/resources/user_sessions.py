from __future__ import annotations

from .._http import resolve_path
from ._base import BaseResource


class UserSessionsResource(BaseResource):
    def delete_many(self, *, ids: list[str], user_id: str) -> None:
        """Ends the caller's sessions named by `ids`, one to 100, the current one included; an id
        that is not the caller's is skipped.

        An API token answers `forbidden`; sign in with a session.
        """
        self._http_client.fetch_status(
            "DELETE",
            resolve_path("/v1/users/{userId}/sessions", userId=user_id),
            query={"ids": ids},
        )
