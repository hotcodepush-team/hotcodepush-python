from __future__ import annotations

from .._http import resolve_path
from .._types import NOT_GIVEN, NotGiven
from ..models import Count, Invitation, InvitationRelation, Member
from ._base import BaseResource


class InvitationsResource(BaseResource):
    """The caller's own invitations, across organizations."""

    def accept(self, *, invitation_id: str, token: str) -> Member:
        """Accepts an invitation addressed to the caller with the token from its mail.

        A repeat answers `invitation_invalid`, so the call is never retried.

        An API token answers `forbidden`; sign in with a session.
        """
        return self._http_client.fetch_json(
            "POST",
            resolve_path("/v1/invitations/{invitationId}/accept", invitationId=invitation_id),
            Member,
            body={"token": token},
        )

    def count(self) -> Count:
        """The number of the caller's pending invitations across organizations.

        An API token answers `forbidden`; sign in with a session.
        """
        return self._http_client.fetch_json("GET", resolve_path("/v1/invitations/count"), Count)

    def list(
        self,
        *,
        limit: int | NotGiven = NOT_GIVEN,
        offset: int | NotGiven = NOT_GIVEN,
        relations: list[InvitationRelation] | NotGiven = NOT_GIVEN,
    ) -> list[Invitation]:
        """The caller's pending invitations across organizations, newest first;
        `relations=["organization"]` embeds each one's organization as its id and name.

        An API token answers `forbidden`; sign in with a session.
        """
        return self._http_client.fetch_json(
            "GET",
            resolve_path("/v1/invitations"),
            list[Invitation],
            query={"limit": limit, "offset": offset, "relations": relations},
        )
