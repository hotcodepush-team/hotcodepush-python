from __future__ import annotations

from .._http import resolve_path
from ._base import BaseResource


class UserPasswordResource(BaseResource):
    def create(self, *, password: str, user_id: str) -> None:
        """Sets the first password of an account that signed up through GitHub, Google or SSO,
        and ends its other sessions.

        An account with a password answers `password_already_set`, as a repeat would, so the
        call is never retried.

        An API token answers `forbidden`; sign in with a session.
        """
        self._http_client.fetch_status(
            "POST",
            resolve_path("/v1/users/{userId}/password", userId=user_id),
            body={"password": password},
        )
