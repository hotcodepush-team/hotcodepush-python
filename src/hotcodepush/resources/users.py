from __future__ import annotations

from .._http import HttpClient, resolve_path
from .._types import NOT_GIVEN, NotGiven
from ..models import User, UserRelation
from ._base import BaseResource
from .user_password import UserPasswordResource
from .user_sessions import UserSessionsResource
from .user_tokens import UserTokensResource


class UsersResource(BaseResource):
    def __init__(self, http_client: HttpClient) -> None:
        super().__init__(http_client)
        self.password = UserPasswordResource(http_client)
        self.sessions = UserSessionsResource(http_client)
        self.tokens = UserTokensResource(http_client)

    def delete(self, *, password: str, user_id: str) -> None:
        """Soft-deletes the caller's account. It is gone at once and hard-deleted after seven days.

        `user_id` takes `me`. `password` is the caller's password. A wrong password answers
        `forbidden`, and so does an account without a password: set one first through
        `users.password.create`.

        An API token answers `forbidden`; sign in with a session.
        """
        self._http_client.fetch_status(
            "DELETE",
            resolve_path("/v1/users/{userId}", userId=user_id),
            body={"password": password},
        )

    def get(self, *, relations: list[UserRelation] | NotGiven = NOT_GIVEN, user_id: str) -> User:
        """Gets the user behind the token.

        `user_id` takes `me`. Any other user answers `forbidden`. `relations` embeds the caller's
        sign-in identities, `accounts`, and member rows in live organizations, `members`. Add
        `members.organization` to embed the organization of each row.
        """
        return self._http_client.fetch_json(
            "GET",
            resolve_path("/v1/users/{userId}", userId=user_id),
            User,
            query={"relations": relations},
        )
