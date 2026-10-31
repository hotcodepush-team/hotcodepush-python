from __future__ import annotations

from .._http import resolve_path
from .._types import NOT_GIVEN, NotGiven
from ..models import BundleDelta, BundleDeltaRelation, Count
from ._base import BaseResource


class BundleDeltasResource(BaseResource):
    def count(self, *, app_id: str, bundle_id: str) -> Count:
        """Counts the delta packs of the bundle."""
        return self._http_client.fetch_json(
            "GET",
            resolve_path(
                "/v1/apps/{appId}/bundles/{bundleId}/deltas/count",
                appId=app_id,
                bundleId=bundle_id,
            ),
            Count,
        )

    def list(
        self,
        *,
        app_id: str,
        bundle_id: str,
        limit: int | NotGiven = NOT_GIVEN,
        offset: int | NotGiven = NOT_GIVEN,
        relations: list[BundleDeltaRelation] | NotGiven = NOT_GIVEN,
    ) -> list[BundleDelta]:
        """Lists the delta packs of the bundle, newest first.

        There is one pack per base bundle that its devices run. `relations=["baseBundle"]`
        embeds the base.
        """
        return self._http_client.fetch_json(
            "GET",
            resolve_path(
                "/v1/apps/{appId}/bundles/{bundleId}/deltas", appId=app_id, bundleId=bundle_id
            ),
            list[BundleDelta],
            query={"limit": limit, "offset": offset, "relations": relations},
        )
