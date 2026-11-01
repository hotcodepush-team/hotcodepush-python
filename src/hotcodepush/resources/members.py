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
        """Counts the members of the organization that match the filters."""
        return self._http_client.fetch_json(
            "GET",
            resolve_path(
                "/v1/organizations/{organizationId}/members/count", organizationId=organization_id
            ),
            query={"query": query, "role": role, "userId": user_id},
            response_type=Count,
        )

    def delete(self, *, member_id: str, organization_id: str) -> None:
        """Removes a member. Any member may remove themselves to leave the organization.

        An API token answers `forbidden`; sign in with a session.
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
        """Removes the members of the organization named by `ids`, 1 to 100.

        An id of another organization is skipped. The whole request is refused if it names the
        Owner.

        An API token answers `forbidden`; sign in with a session.
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
        """Gets a member.

        `relations=["user"]` embeds its user, and `["user", "user.accounts"]` also embeds the
        sign-in identities of the user.
        """
        return self._http_client.fetch_json(
            "GET",
            resolve_path(
                "/v1/organizations/{organizationId}/members/{memberId}",
                memberId=member_id,
                organizationId=organization_id,
            ),
            query={"relations": relations},
            response_type=Member,
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
        """Lists the members of the organization, newest first.

        `query` selects the members whose email contains it.
        """
        return self._http_client.fetch_json(
            "GET",
            resolve_path(
                "/v1/organizations/{organizationId}/members", organizationId=organization_id
            ),
            query={
                "limit": limit,
                "offset": offset,
                "query": query,
                "relations": relations,
                "role": role,
                "userId": user_id,
            },
            response_type=list[Member],
        )

    def update(self, *, member_id: str, organization_id: str, role: Role) -> Member:
        """Changes the role of a member. Setting `owner` transfers the ownership.

        An API token answers `forbidden`; sign in with a session.
        """
        return self._http_client.fetch_json(
            "PATCH",
            resolve_path(
                "/v1/organizations/{organizationId}/members/{memberId}",
                memberId=member_id,
                organizationId=organization_id,
            ),
            body={"role": role},
            response_type=Member,
        )
