from __future__ import annotations

import builtins

from .._http import HttpClient, resolve_path
from .._types import NOT_GIVEN, NotGiven
from ..models import Count, Organization
from ._base import BaseResource
from .audit_logs import AuditLogsResource
from .checkouts import CheckoutsResource
from .customer_portal_sessions import CustomerPortalSessionsResource
from .limits import LimitsResource
from .members import MembersResource
from .organization_apps import OrganizationAppsResource
from .organization_invitations import OrganizationInvitationsResource
from .sso_provider import SsoProviderResource
from .subscription import SubscriptionResource
from .usage import UsageResource
from .webhooks import WebhooksResource


class OrganizationsResource(BaseResource):
    def __init__(self, http_client: HttpClient) -> None:
        super().__init__(http_client)
        self.apps = OrganizationAppsResource(http_client)
        self.audit_logs = AuditLogsResource(http_client)
        self.checkouts = CheckoutsResource(http_client)
        self.customer_portal_sessions = CustomerPortalSessionsResource(http_client)
        self.invitations = OrganizationInvitationsResource(http_client)
        self.limits = LimitsResource(http_client)
        self.members = MembersResource(http_client)
        self.sso_provider = SsoProviderResource(http_client)
        self.subscription = SubscriptionResource(http_client)
        self.usage = UsageResource(http_client)
        self.webhooks = WebhooksResource(http_client)

    def count(self) -> Count:
        """Counts the caller's organizations."""
        return self._http_client.fetch_json(
            "GET", resolve_path("/v1/organizations/count"), response_type=Count
        )

    def create(self, *, idempotency_key: str | NotGiven = NOT_GIVEN, name: str) -> Organization:
        """Creates an organization with the caller as its Owner.

        An API token answers `forbidden`; sign in with a session.
        """
        return self._http_client.fetch_creating_post(
            resolve_path("/v1/organizations"),
            body={"name": name},
            idempotency_key=idempotency_key,
            response_type=Organization,
        )

    def delete(self, *, organization_id: str) -> None:
        """Soft-deletes an organization with everything in it.

        It is gone at once and hard-deleted after seven days.

        An API token answers `forbidden`; sign in with a session.
        """
        self._http_client.fetch_status(
            "DELETE",
            resolve_path("/v1/organizations/{organizationId}", organizationId=organization_id),
        )

    def get(self, *, organization_id: str) -> Organization:
        return self._http_client.fetch_json(
            "GET",
            resolve_path("/v1/organizations/{organizationId}", organizationId=organization_id),
            response_type=Organization,
        )

    def list(
        self, *, limit: int | NotGiven = NOT_GIVEN, offset: int | NotGiven = NOT_GIVEN
    ) -> list[Organization]:
        """Lists the caller's organizations, newest first.

        The caller's role in each is on its member rows:
        `users.get(relations=["members"], user_id="me")`.
        """
        return self._http_client.fetch_json(
            "GET",
            resolve_path("/v1/organizations"),
            query={"limit": limit, "offset": offset},
            response_type=list[Organization],
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
        """Changes the name, the security settings or the spending cap.

        The security settings and the spending cap need a plan that includes them.

        An API token answers `forbidden`; sign in with a session.
        """
        return self._http_client.fetch_json(
            "PATCH",
            resolve_path("/v1/organizations/{organizationId}", organizationId=organization_id),
            body={
                "countryAllowlist": country_allowlist,
                "ipAllowlist": ip_allowlist,
                "isTwoFactorRequired": is_two_factor_required,
                "name": name,
                "spendingCapCents": spending_cap_cents,
            },
            response_type=Organization,
        )
