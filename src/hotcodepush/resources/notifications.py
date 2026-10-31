from __future__ import annotations

from typing import Literal

from .._http import resolve_path
from .._types import NOT_GIVEN, NotGiven
from ..models import Count, Notification, NotificationRelation
from ._base import BaseResource


class NotificationsResource(BaseResource):
    """Your in-app notifications across all organizations."""

    def count(self, *, is_read: bool | NotGiven = NOT_GIVEN) -> Count:
        """Counts your notifications that match the filters.

        `is_read=False` gives the number on the notification bell.

        An API token answers `forbidden`; sign in with a session.
        """
        return self._http_client.fetch_json(
            "GET", resolve_path("/v1/notifications/count"), Count, query={"isRead": is_read}
        )

    def list(
        self,
        *,
        is_read: bool | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        offset: int | NotGiven = NOT_GIVEN,
        relations: list[NotificationRelation] | NotGiven = NOT_GIVEN,
    ) -> list[Notification]:
        """Lists your notifications, newest first.

        An API token answers `forbidden`; sign in with a session.
        """
        return self._http_client.fetch_json(
            "GET",
            resolve_path("/v1/notifications"),
            list[Notification],
            query={"isRead": is_read, "limit": limit, "offset": offset, "relations": relations},
        )

    def update(self, *, is_read: Literal[True], notification_id: str) -> Notification:
        """Marks one of your notifications as read.

        An API token answers `forbidden`; sign in with a session.
        """
        return self._http_client.fetch_json(
            "PATCH",
            resolve_path("/v1/notifications/{notificationId}", notificationId=notification_id),
            Notification,
            body={"isRead": is_read},
        )

    def update_many(self, *, is_read: Literal[True]) -> None:
        """Marks all your unread notifications as read.

        An API token answers `forbidden`; sign in with a session.
        """
        self._http_client.fetch_status(
            "PATCH", resolve_path("/v1/notifications"), body={"isRead": is_read}
        )
