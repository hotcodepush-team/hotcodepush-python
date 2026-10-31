from __future__ import annotations

from .._http import resolve_path
from .._types import NOT_GIVEN, NotGiven
from ..models import Binary, Count, ManifestFile, Platform
from ._base import BaseResource


class BinariesResource(BaseResource):
    def count(
        self,
        *,
        app_id: str,
        fingerprint: str | NotGiven = NOT_GIVEN,
        platform: Platform | NotGiven = NOT_GIVEN,
    ) -> Count:
        """Counts the store builds of the app that match the filters."""
        return self._http_client.fetch_json(
            "GET",
            resolve_path("/v1/apps/{appId}/binaries/count", appId=app_id),
            Count,
            query={"fingerprint": fingerprint, "platform": platform},
        )

    def create(
        self,
        *,
        app_id: str,
        build: str,
        files: list[ManifestFile],
        fingerprint: str | None | NotGiven = NOT_GIVEN,
        force: bool | NotGiven = NOT_GIVEN,
        idempotency_key: str | NotGiven = NOT_GIVEN,
        platform: Platform,
        version: str,
    ) -> Binary:
        """Creates a binary: a store build with the bundle compiled into it.

        Upload its files first. Creating an identical binary again answers the existing one. A
        conflicting fingerprint or file set is refused unless `force` is set.
        """
        return self._http_client.fetch_creating_post(
            resolve_path("/v1/apps/{appId}/binaries", appId=app_id),
            Binary,
            body={
                "build": build,
                "files": files,
                "fingerprint": fingerprint,
                "force": force,
                "platform": platform,
                "version": version,
            },
            idempotency_key=idempotency_key,
        )

    def get(self, *, app_id: str, binary_id: str) -> Binary:
        return self._http_client.fetch_json(
            "GET",
            resolve_path("/v1/apps/{appId}/binaries/{binaryId}", appId=app_id, binaryId=binary_id),
            Binary,
        )

    def list(
        self,
        *,
        app_id: str,
        fingerprint: str | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        offset: int | NotGiven = NOT_GIVEN,
        platform: Platform | NotGiven = NOT_GIVEN,
    ) -> list[Binary]:
        """Lists the store builds of the app, newest first."""
        return self._http_client.fetch_json(
            "GET",
            resolve_path("/v1/apps/{appId}/binaries", appId=app_id),
            list[Binary],
            query={
                "fingerprint": fingerprint,
                "limit": limit,
                "offset": offset,
                "platform": platform,
            },
        )
