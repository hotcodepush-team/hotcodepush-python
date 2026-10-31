from __future__ import annotations

from .._http import resolve_path
from .._types import NOT_GIVEN, NotGiven
from ..models import NotificationCategory, NotificationMedium, NotificationPreference
from ._base import BaseResource


class NotificationPreferencesResource(BaseResource):
    """Your notification preferences, one per category and medium.

    They apply to your account, or to one membership when `organization_id` is set.
    """

    def list(self, *, organization_id: str | NotGiven = NOT_GIVEN) -> list[NotificationPreference]:
        """Lists your notification preferences, defaults included.

        There is one preference per category and per medium the category uses, in catalog order
        with email first. Without `organization_id`, it lists the categories set for the account,
        with it those set per membership.

        An API token answers `forbidden`; sign in with a session.
        """
        return self._http_client.fetch_json(
            "GET",
            resolve_path("/v1/notification-preferences"),
            list[NotificationPreference],
            query={"organizationId": organization_id},
        )

    def update(
        self,
        *,
        category: NotificationCategory,
        is_enabled: bool,
        medium: NotificationMedium,
        organization_id: str | NotGiven = NOT_GIVEN,
    ) -> NotificationPreference:
        """Sets one preference for a category and medium, and returns it.

        The email of a mandatory category is always on.

        An API token answers `forbidden`; sign in with a session.
        """
        return self._http_client.fetch_json(
            "PATCH",
            resolve_path("/v1/notification-preferences"),
            NotificationPreference,
            body={
                "category": category,
                "isEnabled": is_enabled,
                "medium": medium,
                "organizationId": organization_id,
            },
        )
