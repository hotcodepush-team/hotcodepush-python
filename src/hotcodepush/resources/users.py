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
        """Soft-deletes the caller's account: gone at once, hard-deleted after seven days.

        `user_id` takes `me` for the caller; `password` is the account's own, and a wrong one
        answers `E_FORBIDDEN`, as does an account without a password, which sets one first
        through `users.password.create`.

        An API token answers `E_FORBIDDEN`; sign in with a session.
        """
        self._http_client.fetch_status(
            "DELETE",
            resolve_path("/v1/users/{userId}", userId=user_id),
            body={"password": password},
        )

    def get(self, *, relations: list[UserRelation] | NotGiven = NOT_GIVEN, user_id: str) -> User:
        """The caller behind the token; `user_id` takes `me` for the caller, and another user
        answers `E_FORBIDDEN`.

        `relations` embeds the caller's `accounts`, their sign-in identities, their `members` rows
        of live organizations and, with `members.organization`, each row's organization.
        """
        return self._http_client.fetch_json(
            "GET",
            resolve_path("/v1/users/{userId}", userId=user_id),
            User,
            query={"relations": relations},
        )
