from __future__ import annotations

from .._http import resolve_path
from .._types import NOT_GIVEN, NotGiven
from ..models import BundleFile, Count
from ._base import BaseResource


class BundleFilesResource(BaseResource):
    def count(
        self, *, app_id: str, bundle_id: str, is_stored: bool | NotGiven = NOT_GIVEN
    ) -> Count:
        """The number of the bundle's files under the list's filters."""
        return self._http_client.fetch_json(
            "GET",
            resolve_path(
                "/v1/apps/{appId}/bundles/{bundleId}/files/count", appId=app_id, bundleId=bundle_id
            ),
            Count,
            query={"isStored": is_stored},
        )

    def list(
        self,
        *,
        app_id: str,
        bundle_id: str,
        is_stored: bool | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        offset: int | NotGiven = NOT_GIVEN,
    ) -> list[BundleFile]:
        """The bundle's files, ordered by path; an embedded bundle answers the files its binary
        was created with.

        `is_stored=False` selects the files still to upload after the bundle's create.
        """
        return self._http_client.fetch_json(
            "GET",
            resolve_path(
                "/v1/apps/{appId}/bundles/{bundleId}/files", appId=app_id, bundleId=bundle_id
            ),
            list[BundleFile],
            query={"isStored": is_stored, "limit": limit, "offset": offset},
        )
