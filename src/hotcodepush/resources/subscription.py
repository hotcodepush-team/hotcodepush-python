from __future__ import annotations

from typing import Literal

from .._http import resolve_path
from .._types import NOT_GIVEN, NotGiven
from ._base import BaseResource


class SubscriptionResource(BaseResource):
    """The organization's one subscription."""

    def cancel(
        self,
        *,
        comment: str | NotGiven = NOT_GIVEN,
        organization_id: str,
        reason: Literal[
            "missing_features", "not_enough_value", "other", "technical_issues", "too_expensive"
        ],
    ) -> None:
        """Schedules the end of the subscription at the end of its period, with the reason and
        the comment of the retention dialog.

        A cancel already scheduled stays as it is, so the call is retried.

        An API token answers `E_FORBIDDEN`; sign in with a session.
        """
        self._http_client.fetch_status(
            "POST",
            resolve_path(
                "/v1/organizations/{organizationId}/subscription/cancel",
                organizationId=organization_id,
            ),
            body={"comment": comment, "reason": reason},
            is_retryable=True,
        )

    def uncancel(self, *, organization_id: str) -> None:
        """Clears the scheduled end of the subscription, so it renews as before.

        A subscription with no end scheduled stays as it is, so the call is retried.

        An API token answers `E_FORBIDDEN`; sign in with a session.
        """
        self._http_client.fetch_status(
            "POST",
            resolve_path(
                "/v1/organizations/{organizationId}/subscription/uncancel",
                organizationId=organization_id,
            ),
            is_retryable=True,
        )
