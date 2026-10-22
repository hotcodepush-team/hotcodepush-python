from __future__ import annotations

from .._http import resolve_path
from .._types import NOT_GIVEN, NotGiven
from ..models import Count, Member, MemberRelation, Role
from ._base import BaseResource


class MembersResource(BaseResource):
    def count(
        self,
        *,
        organization_id: str,
        query: str | NotGiven = NOT_GIVEN,
        role: Role | NotGiven = NOT_GIVEN,
        user_id: str | NotGiven = NOT_GIVEN,
    ) -> Count:
        """The number of the organization's members under the list's filters."""
        return self._http_client.fetch_json(
            "GET",
            resolve_path(
                "/v1/organizations/{organizationId}/members/count", organizationId=organization_id
            ),
            Count,
            query={"query": query, "role": role, "userId": user_id},
        )

    def delete(self, *, member_id: str, organization_id: str) -> None:
        """Removes a member; any member may remove themselves, which is leaving the organization.

        An API token answers `E_FORBIDDEN`; sign in with a session.
        """
        self._http_client.fetch_status(
            "DELETE",
            resolve_path(
                "/v1/organizations/{organizationId}/members/{memberId}",
                memberId=member_id,
                organizationId=organization_id,
            ),
        )

    def delete_many(self, *, ids: list[str], organization_id: str) -> None:
        """Removes the organization's members named by `ids`, one to 100; an id of another
        organization is skipped, and the Owner refuses the whole set.

        An API token answers `E_FORBIDDEN`; sign in with a session.
        """
        self._http_client.fetch_status(
            "DELETE",
            resolve_path(
                "/v1/organizations/{organizationId}/members", organizationId=organization_id
            ),
            query={"ids": ids},
        )

    def get(
        self,
        *,
        member_id: str,
        organization_id: str,
        relations: list[MemberRelation] | NotGiven = NOT_GIVEN,
    ) -> Member:
        """A member; `relations=["user"]` embeds its user, and `["user", "user.accounts"]` the
        user's sign-in identities under it.
        """
        return self._http_client.fetch_json(
            "GET",
            resolve_path(
                "/v1/organizations/{organizationId}/members/{memberId}",
                memberId=member_id,
                organizationId=organization_id,
            ),
            Member,
            query={"relations": relations},
        )

    def list(
        self,
        *,
        limit: int | NotGiven = NOT_GIVEN,
        offset: int | NotGiven = NOT_GIVEN,
        organization_id: str,
        query: str | NotGiven = NOT_GIVEN,
        relations: list[MemberRelation] | NotGiven = NOT_GIVEN,
        role: Role | NotGiven = NOT_GIVEN,
        user_id: str | NotGiven = NOT_GIVEN,
    ) -> list[Member]:
        """The organization's members, newest first; `query` selects those whose user's email
        contains it.
        """
        return self._http_client.fetch_json(
            "GET",
            resolve_path(
                "/v1/organizations/{organizationId}/members", organizationId=organization_id
            ),
            list[Member],
            query={
                "limit": limit,
                "offset": offset,
                "query": query,
                "relations": relations,
                "role": role,
                "userId": user_id,
            },
        )

    def update(self, *, member_id: str, organization_id: str, role: Role) -> Member:
        """Changes a member's role; setting `owner` transfers the ownership.

        An API token answers `E_FORBIDDEN`; sign in with a session.
        """
        return self._http_client.fetch_json(
            "PATCH",
            resolve_path(
                "/v1/organizations/{organizationId}/members/{memberId}",
                memberId=member_id,
                organizationId=organization_id,
            ),
            Member,
            body={"role": role},
        )
