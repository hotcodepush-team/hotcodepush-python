from __future__ import annotations

from .._http import resolve_path
from .._types import NOT_GIVEN, NotGiven
from ..models import BundleSet, BundleSetRelation, Count, Platform
from ._base import BaseResource


class BundleSetsResource(BaseResource):
    def count(
        self,
        *,
        app_id: str,
        bundle_id: str | NotGiven = NOT_GIVEN,
        bundle_version: str | NotGiven = NOT_GIVEN,
        fingerprint: str | NotGiven = NOT_GIVEN,
        platform: Platform | NotGiven = NOT_GIVEN,
    ) -> Count:
        """Counts the bundle sets of the app that match the filters."""
        return self._http_client.fetch_json(
            method="GET",
            path=resolve_path("/v1/apps/{appId}/bundle-sets/count", appId=app_id),
            query={
                "bundleId": bundle_id,
                "bundleVersion": bundle_version,
                "fingerprint": fingerprint,
                "platform": platform,
            },
            response_type=Count,
        )

    def create(self, *, app_id: str, bundle_ids: list[str]) -> BundleSet:
        """Finds the set of exactly these ready bundles, one per platform, or creates it.

        A new set gets the next number of the app. A set the app already holds answers it
        unchanged, so the call is retried.
        """
        return self._http_client.fetch_json(
            body={"bundleIds": bundle_ids},
            is_retryable=True,
            method="POST",
            path=resolve_path("/v1/apps/{appId}/bundle-sets", appId=app_id),
            response_type=BundleSet,
        )

    def get(
        self,
        *,
        app_id: str,
        bundle_set_id: str,
        relations: list[BundleSetRelation] | NotGiven = NOT_GIVEN,
    ) -> BundleSet:
        return self._http_client.fetch_json(
            method="GET",
            path=resolve_path(
                "/v1/apps/{appId}/bundle-sets/{bundleSetId}",
                appId=app_id,
                bundleSetId=bundle_set_id,
            ),
            query={"relations": relations},
            response_type=BundleSet,
        )

    def list(
        self,
        *,
        app_id: str,
        bundle_id: str | NotGiven = NOT_GIVEN,
        bundle_version: str | NotGiven = NOT_GIVEN,
        fingerprint: str | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        offset: int | NotGiven = NOT_GIVEN,
        platform: Platform | NotGiven = NOT_GIVEN,
        relations: list[BundleSetRelation] | NotGiven = NOT_GIVEN,
    ) -> list[BundleSet]:
        """Lists the bundle sets of the app, newest first.

        `bundle_id` selects the sets that carry the bundle, and `platform` the sets that cover it.
        """
        return self._http_client.fetch_json(
            method="GET",
            path=resolve_path("/v1/apps/{appId}/bundle-sets", appId=app_id),
            query={
                "bundleId": bundle_id,
                "bundleVersion": bundle_version,
                "fingerprint": fingerprint,
                "limit": limit,
                "offset": offset,
                "platform": platform,
                "relations": relations,
            },
            response_type=list[BundleSet],
        )
