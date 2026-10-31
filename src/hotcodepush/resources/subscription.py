from __future__ import annotations

from typing import Literal

from .._http import resolve_path
from .._types import NOT_GIVEN, NotGiven
from ._base import BaseResource


class SubscriptionResource(BaseResource):
    """The one subscription of the organization."""

    def cancel(
        self,
        *,
        comment: str | NotGiven = NOT_GIVEN,
        organization_id: str,
        reason: Literal[
            "missing_features", "not_enough_value", "other", "technical_issues", "too_expensive"
        ],
    ) -> None:
        """Ends the subscription at the end of its current period.

        Pass the reason and comment from the cancellation dialog. Retried, since a scheduled
        cancellation stays as it is.

        An API token answers `forbidden`; sign in with a session.
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
        """Removes the scheduled end of the subscription, so it renews as before.

        Retried, since a subscription without a scheduled end stays as it is.

        An API token answers `forbidden`; sign in with a session.
        """
        self._http_client.fetch_status(
            "POST",
            resolve_path(
                "/v1/organizations/{organizationId}/subscription/uncancel",
                organizationId=organization_id,
            ),
            is_retryable=True,
        )
