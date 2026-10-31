from __future__ import annotations

from .._http import resolve_path
from ._base import BaseResource


class UserTokensResource(BaseResource):
    def delete_many(self, *, ids: list[str], user_id: str) -> None:
        """Deletes your API tokens named by `ids`, 1 to 100.

        An id that is not yours is skipped.

        An API token answers `forbidden`; sign in with a session.
        """
        self._http_client.fetch_status(
            "DELETE",
            resolve_path("/v1/users/{userId}/tokens", userId=user_id),
            query={"ids": ids},
        )
