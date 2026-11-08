from __future__ import annotations

from .._http import resolve_path
from .._types import NOT_GIVEN, NotGiven
from ..models import Platform, Release
from ._base import BaseResource


class RollbacksResource(BaseResource):
    def create(
        self,
        *,
        app_id: str,
        channel_id: str,
        idempotency_key: str | NotGiven = NOT_GIVEN,
        is_mandatory: bool | NotGiven = NOT_GIVEN,
        platform: Platform | None | NotGiven = NOT_GIVEN,
        to_release_id: str | None | NotGiven = NOT_GIVEN,
    ) -> Release:
        """Rolls the channel back to the release before its newest active one.

        `platform` undoes the newest active release that serves it. `to_release_id` picks another
        earlier release instead. A rollback is a new release.
        """
        return self._http_client.fetch_creating_post(
            body={"isMandatory": is_mandatory, "platform": platform, "toReleaseId": to_release_id},
            idempotency_key=idempotency_key,
            path=resolve_path(
                "/v1/apps/{appId}/channels/{channelId}/rollbacks",
                appId=app_id,
                channelId=channel_id,
            ),
            response_type=Release,
        )
