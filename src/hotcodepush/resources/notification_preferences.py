from __future__ import annotations

from .._http import resolve_path
from .._types import NOT_GIVEN, NotGiven
from ..models import NotificationCategory, NotificationMedium, NotificationPreference
from ._base import BaseResource


class NotificationPreferencesResource(BaseResource):
    """The caller's notification preferences, one per category and medium, for the account or,
    with `organization_id`, for that membership.
    """

    def list(self, *, organization_id: str | NotGiven = NOT_GIVEN) -> list[NotificationPreference]:
        """One preference per category and each medium its notifications reach, the defaults
        included, in the catalog's order and email first: the categories set for the account, or
        with `organization_id` those set per membership.

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
        """Sets one preference, the category and the medium, and answers it; a mandatory
        category's email is always on.

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
