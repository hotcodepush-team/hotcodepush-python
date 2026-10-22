from __future__ import annotations

from .._http import resolve_path
from ..models import Audience
from ._base import BaseResource


class ReleaseAudienceResource(BaseResource):
    def get(self, *, app_id: str, release_id: str) -> Audience:
        """The devices a release reaches, evaluated over the registry the way the device
        evaluates the index.
        """
        return self._http_client.fetch_json(
            "GET",
            resolve_path(
                "/v1/apps/{appId}/releases/{releaseId}/audience",
                appId=app_id,
                releaseId=release_id,
            ),
            Audience,
        )
