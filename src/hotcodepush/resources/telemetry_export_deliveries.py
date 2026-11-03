from __future__ import annotations

from datetime import datetime

from .._http import resolve_path
from .._types import NOT_GIVEN, NotGiven
from ..models import Count, Delivery, DeliveryStatus
from ._base import BaseResource


class TelemetryExportDeliveriesResource(BaseResource):
    """The delivery log of the telemetry export. Each delivery is kept for 30 days."""

    def count(
        self,
        *,
        created_since: datetime | NotGiven = NOT_GIVEN,
        created_until: datetime | NotGiven = NOT_GIVEN,
        organization_id: str,
        status: DeliveryStatus | NotGiven = NOT_GIVEN,
    ) -> Count:
        """Counts the deliveries of the telemetry export that match the filters.

        An API token answers `forbidden`; sign in with a session.
        """
        return self._http_client.fetch_json(
            method="GET",
            path=resolve_path(
                "/v1/organizations/{organizationId}/telemetry-export/deliveries/count",
                organizationId=organization_id,
            ),
            query={"createdSince": created_since, "createdUntil": created_until, "status": status},
            response_type=Count,
        )

    def list(
        self,
        *,
        created_since: datetime | NotGiven = NOT_GIVEN,
        created_until: datetime | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        offset: int | NotGiven = NOT_GIVEN,
        organization_id: str,
        status: DeliveryStatus | NotGiven = NOT_GIVEN,
    ) -> list[Delivery]:
        """Lists the deliveries of the telemetry export, newest first.

        `status` filters by status. `created_since` and `created_until` filter by creation time,
        both inclusive.

        An API token answers `forbidden`; sign in with a session.
        """
        return self._http_client.fetch_json(
            method="GET",
            path=resolve_path(
                "/v1/organizations/{organizationId}/telemetry-export/deliveries",
                organizationId=organization_id,
            ),
            query={
                "createdSince": created_since,
                "createdUntil": created_until,
                "limit": limit,
                "offset": offset,
                "status": status,
            },
            response_type=list[Delivery],
        )

    def redeliver(self, *, delivery_id: str, organization_id: str) -> Delivery:
        """Sends the record again, once, and returns the settled delivery.

        The attempt runs within the request, and the attempt count goes on from before. Never
        retried, since each call makes another attempt.

        An API token answers `forbidden`; sign in with a session.
        """
        return self._http_client.fetch_json(
            method="POST",
            path=resolve_path(
                "/v1/organizations/{organizationId}/telemetry-export/deliveries/{deliveryId}/redeliver",
                deliveryId=delivery_id,
                organizationId=organization_id,
            ),
            response_type=Delivery,
        )
