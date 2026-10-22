from __future__ import annotations

from .._http import resolve_path
from .._types import NOT_GIVEN, NotGiven
from ..models import Release
from ._base import BaseResource


class RollbacksResource(BaseResource):
    def create(
        self,
        *,
        app_id: str,
        channel_id: str,
        idempotency_key: str | NotGiven = NOT_GIVEN,
        is_mandatory: bool | NotGiven = NOT_GIVEN,
        to_release_id: str | None | NotGiven = NOT_GIVEN,
    ) -> Release:
        """Releases the channel's previous bundle again, or the one of `to_release_id`; a
        rollback is a new release.
        """
        return self._http_client.fetch_creating_post(
            resolve_path(
                "/v1/apps/{appId}/channels/{channelId}/rollbacks",
                appId=app_id,
                channelId=channel_id,
            ),
            Release,
            body={"isMandatory": is_mandatory, "toReleaseId": to_release_id},
            idempotency_key=idempotency_key,
        )
