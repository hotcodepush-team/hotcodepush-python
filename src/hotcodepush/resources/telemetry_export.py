from __future__ import annotations

from .._http import HttpClient, resolve_path
from ..models import Delivery, TelemetryExport, TelemetrySignal
from ._base import BaseResource
from .telemetry_export_deliveries import TelemetryExportDeliveriesResource


class TelemetryExportResource(BaseResource):
    """The one telemetry export of the organization, for Admins and Owners.

    It sends the audit log and the metrics to an OTLP/HTTP endpoint. Setting, switching, testing
    and redelivering need a paying plan, otherwise the API answers `plan_required`.
    """

    def __init__(self, http_client: HttpClient) -> None:
        super().__init__(http_client)
        self.deliveries = TelemetryExportDeliveriesResource(http_client)

    def delete(self, *, organization_id: str) -> None:
        """Removes the telemetry export with its delivery log, on any plan.

        An API token answers `forbidden`; sign in with a session.
        """
        self._http_client.fetch_status(
            method="DELETE",
            path=resolve_path(
                "/v1/organizations/{organizationId}/telemetry-export",
                organizationId=organization_id,
            ),
        )

    def get(self, *, organization_id: str) -> TelemetryExport:
        """Gets the telemetry export. Without one, the API answers `not_found`.

        An API token answers `forbidden`; sign in with a session.
        """
        return self._http_client.fetch_json(
            method="GET",
            path=resolve_path(
                "/v1/organizations/{organizationId}/telemetry-export",
                organizationId=organization_id,
            ),
            response_type=TelemetryExport,
        )

    def set(
        self,
        *,
        headers: dict[str, str],
        organization_id: str,
        signals: list[TelemetrySignal],
        url: str,
    ) -> TelemetryExport:
        """Sets the telemetry export, replacing the one before. It starts enabled.

        `url` is the OTLP/HTTP base URL, without `/v1/logs` or `/v1/metrics`. `headers`, at most
        16, carry the vendor's credentials and are never answered again.

        An API token answers `forbidden`; sign in with a session.
        """
        return self._http_client.fetch_json(
            body={"headers": headers, "signals": signals, "url": url},
            method="PUT",
            path=resolve_path(
                "/v1/organizations/{organizationId}/telemetry-export",
                organizationId=organization_id,
            ),
            response_type=TelemetryExport,
        )

    def test(self, *, organization_id: str) -> list[Delivery]:
        """Sends one delivery per signal, once, and returns the settled deliveries.

        A `telemetry_export.test` log record goes to `/v1/logs` and the current metrics to
        `/v1/metrics`. Never retried, since each call sends them again.

        An API token answers `forbidden`; sign in with a session.
        """
        return self._http_client.fetch_json(
            method="POST",
            path=resolve_path(
                "/v1/organizations/{organizationId}/telemetry-export/test",
                organizationId=organization_id,
            ),
            response_type=list[Delivery],
        )

    def update(self, *, is_enabled: bool, organization_id: str) -> TelemetryExport:
        """Turns the telemetry export on or off.

        `is_enabled=False` sets `disabled_at`, and `is_enabled=True` clears it and resets the
        failure count.

        An API token answers `forbidden`; sign in with a session.
        """
        return self._http_client.fetch_json(
            body={"isEnabled": is_enabled},
            method="PATCH",
            path=resolve_path(
                "/v1/organizations/{organizationId}/telemetry-export",
                organizationId=organization_id,
            ),
            response_type=TelemetryExport,
        )
