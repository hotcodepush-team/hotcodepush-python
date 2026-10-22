from __future__ import annotations

from datetime import datetime
from typing import Literal

from .._http import resolve_path
from .._types import NOT_GIVEN, NotGiven
from ..models import Count, WebhookDelivery
from ._base import BaseResource


class WebhookDeliveriesResource(BaseResource):
    """A webhook's delivery log, each delivery kept for 30 days."""

    def count(
        self,
        *,
        created_since: datetime | NotGiven = NOT_GIVEN,
        created_until: datetime | NotGiven = NOT_GIVEN,
        organization_id: str,
        status: Literal["failed", "pending", "succeeded"] | NotGiven = NOT_GIVEN,
        webhook_id: str,
    ) -> Count:
        """The number of the webhook's deliveries under the list's filters.

        An API token answers `E_FORBIDDEN`; sign in with a session.
        """
        return self._http_client.fetch_json(
            "GET",
            resolve_path(
                "/v1/organizations/{organizationId}/webhooks/{webhookId}/deliveries/count",
                organizationId=organization_id,
                webhookId=webhook_id,
            ),
            Count,
            query={"createdSince": created_since, "createdUntil": created_until, "status": status},
        )

    def list(
        self,
        *,
        created_since: datetime | NotGiven = NOT_GIVEN,
        created_until: datetime | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        offset: int | NotGiven = NOT_GIVEN,
        organization_id: str,
        status: Literal["failed", "pending", "succeeded"] | NotGiven = NOT_GIVEN,
        webhook_id: str,
    ) -> list[WebhookDelivery]:
        """The webhook's deliveries, newest first, filtered by `status` and by `created_since` and
        `created_until`, both inclusive.

        An API token answers `E_FORBIDDEN`; sign in with a session.
        """
        return self._http_client.fetch_json(
            "GET",
            resolve_path(
                "/v1/organizations/{organizationId}/webhooks/{webhookId}/deliveries",
                organizationId=organization_id,
                webhookId=webhook_id,
            ),
            list[WebhookDelivery],
            query={
                "createdSince": created_since,
                "createdUntil": created_until,
                "limit": limit,
                "offset": offset,
                "status": status,
            },
        )

    def redeliver(
        self, *, delivery_id: str, organization_id: str, webhook_id: str
    ) -> WebhookDelivery:
        """Delivers the event again, once, within the request, and answers the settled delivery,
        its attempt count carried on.

        Each call makes another attempt, so the call is never retried.

        An API token answers `E_FORBIDDEN`; sign in with a session.
        """
        return self._http_client.fetch_json(
            "POST",
            resolve_path(
                "/v1/organizations/{organizationId}/webhooks/{webhookId}/deliveries/{deliveryId}/redeliver",
                deliveryId=delivery_id,
                organizationId=organization_id,
                webhookId=webhook_id,
            ),
            WebhookDelivery,
        )
