from __future__ import annotations

import builtins

from .._http import HttpClient, resolve_path
from .._types import NOT_GIVEN, NotGiven
from ..models import Count, Organization
from ._base import BaseResource
from .organization_apps import OrganizationAppsResource


class OrganizationsResource(BaseResource):
    def __init__(self, http_client: HttpClient) -> None:
        super().__init__(http_client)
        self.apps = OrganizationAppsResource(http_client)

    def count(self) -> Count:
        """The number of the caller's organizations."""
        return self._http_client.fetch_json("GET", resolve_path("/v1/organizations/count"), Count)

    def create(self, *, idempotency_key: str | NotGiven = NOT_GIVEN, name: str) -> Organization:
        """Creates an organization with the caller as its Owner.

        An API token answers `E_FORBIDDEN`; sign in with a session.
        """
        return self._http_client.fetch_creating_post(
            resolve_path("/v1/organizations"),
            Organization,
            body={"name": name},
            idempotency_key=idempotency_key,
        )

    def delete(self, *, organization_id: str) -> None:
        """Soft-deletes an organization with everything under it: gone at once, hard-deleted
        after seven days.

        An API token answers `E_FORBIDDEN`; sign in with a session.
        """
        self._http_client.fetch_status(
            "DELETE",
            resolve_path("/v1/organizations/{organizationId}", organizationId=organization_id),
        )

    def get(self, *, organization_id: str) -> Organization:
        return self._http_client.fetch_json(
            "GET",
            resolve_path("/v1/organizations/{organizationId}", organizationId=organization_id),
            Organization,
        )

    def list(
        self, *, limit: int | NotGiven = NOT_GIVEN, offset: int | NotGiven = NOT_GIVEN
    ) -> list[Organization]:
        """The caller's organizations, newest first; the caller's role in each is on their
        member rows, `users.get(relations=["members"], user_id="me")`.
        """
        return self._http_client.fetch_json(
            "GET",
            resolve_path("/v1/organizations"),
            list[Organization],
            query={"limit": limit, "offset": offset},
        )

    def update(
        self,
        *,
        country_allowlist: builtins.list[str] | None | NotGiven = NOT_GIVEN,
        ip_allowlist: builtins.list[str] | None | NotGiven = NOT_GIVEN,
        is_two_factor_required: bool | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        organization_id: str,
        spending_cap_cents: int | NotGiven = NOT_GIVEN,
    ) -> Organization:
        """Changes the name, the security settings and the spending cap; the security settings
        and the cap need a paying plan.

        An API token answers `E_FORBIDDEN`; sign in with a session.
        """
        return self._http_client.fetch_json(
            "PATCH",
            resolve_path("/v1/organizations/{organizationId}", organizationId=organization_id),
            Organization,
            body={
                "countryAllowlist": country_allowlist,
                "ipAllowlist": ip_allowlist,
                "isTwoFactorRequired": is_two_factor_required,
                "name": name,
                "spendingCapCents": spending_cap_cents,
            },
        )
