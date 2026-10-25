from __future__ import annotations

import builtins
from typing import Literal

from .._http import HttpClient, resolve_path
from .._types import NOT_GIVEN, NotGiven
from ..models import Count, CreatedWebhook, Webhook, WebhookDelivery, WebhookEvent
from ._base import BaseResource
from .webhook_deliveries import WebhookDeliveriesResource


class WebhooksResource(BaseResource):
    """The organization's webhooks, for Admins and Owners on a plan that includes them; any
    other plan answers `plan_required`.
    """

    def __init__(self, http_client: HttpClient) -> None:
        super().__init__(http_client)
        self.deliveries = WebhookDeliveriesResource(http_client)

    def count(self, *, organization_id: str) -> Count:
        """The number of the organization's webhooks.

        An API token answers `forbidden`; sign in with a session.
        """
        return self._http_client.fetch_json(
            "GET",
            resolve_path(
                "/v1/organizations/{organizationId}/webhooks/count", organizationId=organization_id
            ),
            Count,
        )

    def create(
        self,
        *,
        app_id: str | None | NotGiven = NOT_GIVEN,
        events: list[WebhookEvent],
        format: Literal["discord", "raw", "slack", "teams"],
        name: str,
        organization_id: str,
        url: str,
    ) -> CreatedWebhook:
        """Creates a webhook, its name unique in the organization, `webhook_name_taken`
        otherwise; a `raw` webhook answers its secret this once.

        The API keeps no `Idempotency-Key` for it and a repeat answers `webhook_name_taken`, so
        the call is never retried.

        An API token answers `forbidden`; sign in with a session.
        """
        return self._http_client.fetch_json(
            "POST",
            resolve_path(
                "/v1/organizations/{organizationId}/webhooks", organizationId=organization_id
            ),
            CreatedWebhook,
            body={"appId": app_id, "events": events, "format": format, "name": name, "url": url},
        )

    def delete(self, *, organization_id: str, webhook_id: str) -> None:
        """Deletes the webhook with its delivery log.

        An API token answers `forbidden`; sign in with a session.
        """
        self._http_client.fetch_status(
            "DELETE",
            resolve_path(
                "/v1/organizations/{organizationId}/webhooks/{webhookId}",
                organizationId=organization_id,
                webhookId=webhook_id,
            ),
        )

    def get(self, *, organization_id: str, webhook_id: str) -> Webhook:
        """An API token answers `forbidden`; sign in with a session."""
        return self._http_client.fetch_json(
            "GET",
            resolve_path(
                "/v1/organizations/{organizationId}/webhooks/{webhookId}",
                organizationId=organization_id,
                webhookId=webhook_id,
            ),
            Webhook,
        )

    def list(
        self,
        *,
        limit: int | NotGiven = NOT_GIVEN,
        offset: int | NotGiven = NOT_GIVEN,
        organization_id: str,
    ) -> list[Webhook]:
        """The organization's webhooks, newest first.

        An API token answers `forbidden`; sign in with a session.
        """
        return self._http_client.fetch_json(
            "GET",
            resolve_path(
                "/v1/organizations/{organizationId}/webhooks", organizationId=organization_id
            ),
            list[Webhook],
            query={"limit": limit, "offset": offset},
        )

    def test(self, *, organization_id: str, webhook_id: str) -> WebhookDelivery:
        """Sends one sample event, `webhook.test`, through the webhook's delivery path within the
        request and answers the settled delivery.

        Each call sends another sample event, so the call is never retried.

        An API token answers `forbidden`; sign in with a session.
        """
        return self._http_client.fetch_json(
            "POST",
            resolve_path(
                "/v1/organizations/{organizationId}/webhooks/{webhookId}/test",
                organizationId=organization_id,
                webhookId=webhook_id,
            ),
            WebhookDelivery,
        )

    def update(
        self,
        *,
        app_id: str | None | NotGiven = NOT_GIVEN,
        events: builtins.list[WebhookEvent] | NotGiven = NOT_GIVEN,
        is_enabled: bool | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        organization_id: str,
        url: str | NotGiven = NOT_GIVEN,
        webhook_id: str,
    ) -> Webhook:
        """Changes the name, the URL, the subscribed `events`, the app filter or `is_enabled`; the
        format and the secret never change. Setting `is_enabled` on a webhook disabled after fifty
        consecutive failed deliveries starts its count again.

        An API token answers `forbidden`; sign in with a session.
        """
        return self._http_client.fetch_json(
            "PATCH",
            resolve_path(
                "/v1/organizations/{organizationId}/webhooks/{webhookId}",
                organizationId=organization_id,
                webhookId=webhook_id,
            ),
            Webhook,
            body={
                "appId": app_id,
                "events": events,
                "isEnabled": is_enabled,
                "name": name,
                "url": url,
            },
        )
