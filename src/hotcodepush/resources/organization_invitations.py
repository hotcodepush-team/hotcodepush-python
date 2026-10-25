from __future__ import annotations

from typing import Literal

from .._http import resolve_path
from .._types import NOT_GIVEN, NotGiven
from ..models import Count, Invitation, InvitationRole, Role
from ._base import BaseResource


class OrganizationInvitationsResource(BaseResource):
    def count(
        self,
        *,
        organization_id: str,
        query: str | NotGiven = NOT_GIVEN,
        role: Role | NotGiven = NOT_GIVEN,
        status: Literal["pending"] | NotGiven = NOT_GIVEN,
    ) -> Count:
        """The number of the organization's invitations under the list's filters.

        An API token answers `forbidden`; sign in with a session.
        """
        return self._http_client.fetch_json(
            "GET",
            resolve_path(
                "/v1/organizations/{organizationId}/invitations/count",
                organizationId=organization_id,
            ),
            Count,
            query={"query": query, "role": role, "status": status},
        )

    def create(
        self,
        *,
        email: str,
        idempotency_key: str | NotGiven = NOT_GIVEN,
        organization_id: str,
        role: InvitationRole | NotGiven = NOT_GIVEN,
    ) -> Invitation:
        """Invites an address to the organization, as a Member unless `role` says otherwise; the
        invitation mail carries the token.

        An API token answers `forbidden`; sign in with a session.
        """
        return self._http_client.fetch_creating_post(
            resolve_path(
                "/v1/organizations/{organizationId}/invitations", organizationId=organization_id
            ),
            Invitation,
            body={"email": email, "role": role},
            idempotency_key=idempotency_key,
        )

    def delete(self, *, invitation_id: str, organization_id: str) -> None:
        """Withdraws an invitation.

        An API token answers `forbidden`; sign in with a session.
        """
        self._http_client.fetch_status(
            "DELETE",
            resolve_path(
                "/v1/organizations/{organizationId}/invitations/{invitationId}",
                invitationId=invitation_id,
                organizationId=organization_id,
            ),
        )

    def delete_many(self, *, ids: list[str], organization_id: str) -> None:
        """Withdraws the organization's invitations named by `ids`, one to 100; an id of another
        organization is skipped.

        An API token answers `forbidden`; sign in with a session.
        """
        self._http_client.fetch_status(
            "DELETE",
            resolve_path(
                "/v1/organizations/{organizationId}/invitations", organizationId=organization_id
            ),
            query={"ids": ids},
        )

    def list(
        self,
        *,
        limit: int | NotGiven = NOT_GIVEN,
        offset: int | NotGiven = NOT_GIVEN,
        organization_id: str,
        query: str | NotGiven = NOT_GIVEN,
        role: Role | NotGiven = NOT_GIVEN,
        status: Literal["pending"] | NotGiven = NOT_GIVEN,
    ) -> list[Invitation]:
        """The organization's invitations, newest first; `query` selects those whose email
        contains it, and `status="pending"` those still pending and not yet expired.

        An API token answers `forbidden`; sign in with a session.
        """
        return self._http_client.fetch_json(
            "GET",
            resolve_path(
                "/v1/organizations/{organizationId}/invitations", organizationId=organization_id
            ),
            list[Invitation],
            query={
                "limit": limit,
                "offset": offset,
                "query": query,
                "role": role,
                "status": status,
            },
        )
