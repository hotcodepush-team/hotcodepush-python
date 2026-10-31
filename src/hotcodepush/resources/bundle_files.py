from __future__ import annotations

from .._http import resolve_path
from .._types import NOT_GIVEN, NotGiven
from ..models import BundleFile, Count
from ._base import BaseResource


class BundleFilesResource(BaseResource):
    def count(
        self, *, app_id: str, bundle_id: str, is_stored: bool | NotGiven = NOT_GIVEN
    ) -> Count:
        """Counts the files of the bundle that match the filters."""
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
        """Lists the files of the bundle, ordered by path.

        For an embedded bundle, these are the files its binary was created with. `is_stored=False`
        selects the files that still need an upload after the bundle is created.
        """
        return self._http_client.fetch_json(
            "GET",
            resolve_path(
                "/v1/apps/{appId}/bundles/{bundleId}/files", appId=app_id, bundleId=bundle_id
            ),
            list[BundleFile],
            query={"isStored": is_stored, "limit": limit, "offset": offset},
        )
