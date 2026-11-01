from __future__ import annotations

from typing import Literal

from .._http import HttpClient, resolve_path
from .._types import NOT_GIVEN, NotGiven
from ..models import Bundle, BundleSignature, Count, ManifestFile, Platform
from ._base import BaseResource
from .bundle_deltas import BundleDeltasResource
from .bundle_files import BundleFilesResource
from .bundle_pack import BundlePackResource


class BundlesResource(BaseResource):
    def __init__(self, http_client: HttpClient) -> None:
        super().__init__(http_client)
        self.deltas = BundleDeltasResource(http_client)
        self.files = BundleFilesResource(http_client)
        self.pack = BundlePackResource(http_client)

    def complete(self, *, app_id: str, bundle_id: str) -> Bundle:
        """Completes a bundle and sets it `ready`.

        The API checks that every listed file and the pack are uploaded, then writes the manifest.
        Retried, since a completed bundle answers itself again.
        """
        return self._http_client.fetch_json(
            "POST",
            resolve_path(
                "/v1/apps/{appId}/bundles/{bundleId}/complete", appId=app_id, bundleId=bundle_id
            ),
            is_retryable=True,
            response_type=Bundle,
        )

    def count(
        self,
        *,
        app_id: str,
        fingerprint: str | NotGiven = NOT_GIVEN,
        is_in_use: bool | NotGiven = NOT_GIVEN,
        platform: Platform | NotGiven = NOT_GIVEN,
        query: str | NotGiven = NOT_GIVEN,
        source: Literal["binary", "upload"] | NotGiven = NOT_GIVEN,
        status: Literal["ready", "uploading"] | NotGiven = NOT_GIVEN,
        version: str | NotGiven = NOT_GIVEN,
    ) -> Count:
        """Counts the bundles of the app that match the filters."""
        return self._http_client.fetch_json(
            "GET",
            resolve_path("/v1/apps/{appId}/bundles/count", appId=app_id),
            query={
                "fingerprint": fingerprint,
                "isInUse": is_in_use,
                "platform": platform,
                "query": query,
                "source": source,
                "status": status,
                "version": version,
            },
            response_type=Count,
        )

    def create(
        self,
        *,
        app_id: str,
        files: list[ManifestFile],
        fingerprint: str | None | NotGiven = NOT_GIVEN,
        git_message: str | None | NotGiven = NOT_GIVEN,
        git_ref: str | None | NotGiven = NOT_GIVEN,
        git_remote: str | None | NotGiven = NOT_GIVEN,
        git_sha: str | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | NotGiven = NOT_GIVEN,
        is_git_dirty: bool | None | NotGiven = NOT_GIVEN,
        platforms: list[Platform],
        signature: BundleSignature | None | NotGiven = NOT_GIVEN,
        version: str,
    ) -> Bundle:
        """Creates a bundle from its manifest. It stays `uploading` until it is completed.

        `apps.bundles.files.list` with `is_stored=False` names the files the app lacks. Upload each
        through `apps.files.upload`, and the pack through `apps.bundles.pack.upload`.
        """
        return self._http_client.fetch_creating_post(
            resolve_path("/v1/apps/{appId}/bundles", appId=app_id),
            body={
                "files": files,
                "fingerprint": fingerprint,
                "gitMessage": git_message,
                "gitRef": git_ref,
                "gitRemote": git_remote,
                "gitSha": git_sha,
                "isGitDirty": is_git_dirty,
                "platforms": platforms,
                "signature": signature,
                "version": version,
            },
            idempotency_key=idempotency_key,
            response_type=Bundle,
        )

    def delete(self, *, app_id: str, bundle_id: str) -> None:
        """Deletes a bundle at once.

        A bundle that a release serves or a store build embeds is refused.
        """
        self._http_client.fetch_status(
            "DELETE",
            resolve_path("/v1/apps/{appId}/bundles/{bundleId}", appId=app_id, bundleId=bundle_id),
        )

    def get(self, *, app_id: str, bundle_id: str) -> Bundle:
        return self._http_client.fetch_json(
            "GET",
            resolve_path("/v1/apps/{appId}/bundles/{bundleId}", appId=app_id, bundleId=bundle_id),
            response_type=Bundle,
        )

    def list(
        self,
        *,
        app_id: str,
        fingerprint: str | NotGiven = NOT_GIVEN,
        is_in_use: bool | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        offset: int | NotGiven = NOT_GIVEN,
        platform: Platform | NotGiven = NOT_GIVEN,
        query: str | NotGiven = NOT_GIVEN,
        source: Literal["binary", "upload"] | NotGiven = NOT_GIVEN,
        status: Literal["ready", "uploading"] | NotGiven = NOT_GIVEN,
        version: str | NotGiven = NOT_GIVEN,
    ) -> list[Bundle]:
        """Lists the bundles of the app, newest first."""
        return self._http_client.fetch_json(
            "GET",
            resolve_path("/v1/apps/{appId}/bundles", appId=app_id),
            query={
                "fingerprint": fingerprint,
                "isInUse": is_in_use,
                "limit": limit,
                "offset": offset,
                "platform": platform,
                "query": query,
                "source": source,
                "status": status,
                "version": version,
            },
            response_type=list[Bundle],
        )
