from __future__ import annotations

from typing import Literal

from .._http import resolve_path
from .._types import NOT_GIVEN, NotGiven
from ..models import Count, Notification, NotificationRelation
from ._base import BaseResource


class NotificationsResource(BaseResource):
    """The caller's in-app notifications across all organizations."""

    def count(self, *, is_read: bool | NotGiven = NOT_GIVEN) -> Count:
        """Counts the caller's notifications that match the filters.

        `is_read=False` gives the number on the notification bell.

        An API token answers `forbidden`; sign in with a session.
        """
        return self._http_client.fetch_json(
            "GET",
            resolve_path("/v1/notifications/count"),
            query={"isRead": is_read},
            response_type=Count,
        )

    def list(
        self,
        *,
        is_read: bool | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        offset: int | NotGiven = NOT_GIVEN,
        relations: list[NotificationRelation] | NotGiven = NOT_GIVEN,
    ) -> list[Notification]:
        """Lists the caller's notifications, newest first.

        An API token answers `forbidden`; sign in with a session.
        """
        return self._http_client.fetch_json(
            "GET",
            resolve_path("/v1/notifications"),
            query={"isRead": is_read, "limit": limit, "offset": offset, "relations": relations},
            response_type=list[Notification],
        )

    def update(self, *, is_read: Literal[True], notification_id: str) -> Notification:
        """Marks one of the caller's notifications as read.

        An API token answers `forbidden`; sign in with a session.
        """
        return self._http_client.fetch_json(
            "PATCH",
            resolve_path("/v1/notifications/{notificationId}", notificationId=notification_id),
            body={"isRead": is_read},
            response_type=Notification,
        )

    def update_many(self, *, is_read: Literal[True]) -> None:
        """Marks all unread notifications of the caller as read.

        An API token answers `forbidden`; sign in with a session.
        """
        self._http_client.fetch_status(
            "PATCH", resolve_path("/v1/notifications"), body={"isRead": is_read}
        )
