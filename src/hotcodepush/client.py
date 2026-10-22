"""The client for the HotCodePush REST API."""

from __future__ import annotations

import os
from types import TracebackType

import httpx

from ._http import DEFAULT_BASE_URL, DEFAULT_CLIENT, HttpClient
from .resources.apps import AppsResource
from .resources.health import HealthResource
from .resources.invitations import InvitationsResource
from .resources.notification_preferences import NotificationPreferencesResource
from .resources.notifications import NotificationsResource
from .resources.organizations import OrganizationsResource
from .resources.users import UsersResource

TOKEN_ENVIRONMENT_VARIABLE = "HOTCODEPUSH_TOKEN"


class HotCodePush:
    """The client for the HotCodePush REST API.

    Resources mirror the paths: `/v1/organizations/{organizationId}/apps` is
    `organizations.apps`, `/v1/apps/{appId}/channels` is `apps.channels`.

    Args:
        token: The API token, sent as `Authorization: Bearer <token>`; falls back to the
            `HOTCODEPUSH_TOKEN` environment variable and stays optional, since `/health` needs
            none.
        base_url: The base URL of the API.
        client: The `X-HotCodePush-Client` header, `<name>/<version>`.
        http_client: The `httpx.Client` that sends the requests in place of the client's own;
            `close` leaves it open.
        timeout: The seconds every phase of a JSON call's attempt may take, httpx's connect,
            read, write and pool timeouts; sixty when unset. An upload attempt gets ten minutes.
        user_agent: The `User-Agent` header, sent only when set, since a session keeps it and
            the sessions page names the client by it.
    """

    def __init__(
        self,
        token: str | None = None,
        *,
        base_url: str = DEFAULT_BASE_URL,
        client: str = DEFAULT_CLIENT,
        http_client: httpx.Client | None = None,
        timeout: float | None = None,
        user_agent: str | None = None,
    ) -> None:
        self._http_client = HttpClient(
            base_url=base_url,
            client=client,
            http_client=http_client,
            timeout=timeout,
            token=token or os.environ.get(TOKEN_ENVIRONMENT_VARIABLE),
            user_agent=user_agent,
        )
        self.apps = AppsResource(self._http_client)
        self.health = HealthResource(self._http_client)
        self.invitations = InvitationsResource(self._http_client)
        self.notification_preferences = NotificationPreferencesResource(self._http_client)
        self.notifications = NotificationsResource(self._http_client)
        self.organizations = OrganizationsResource(self._http_client)
        self.users = UsersResource(self._http_client)

    def close(self) -> None:
        """Closes the connection pool, unless the requests go through the caller's `http_client`."""
        self._http_client.close()

    def __enter__(self) -> HotCodePush:
        return self

    def __exit__(
        self,
        exception_type: type[BaseException] | None,
        exception: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()
