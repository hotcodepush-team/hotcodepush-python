from __future__ import annotations

from typing import Literal

from .._http import HttpClient, resolve_path
from .._types import NOT_GIVEN, NotGiven
from ..models import Count, FailureAction, Release, ReleaseProgression, ReleaseRelation
from ._base import BaseResource
from .release_audience import ReleaseAudienceResource


class ReleasesResource(BaseResource):
    def __init__(self, http_client: HttpClient) -> None:
        super().__init__(http_client)
        self.audience = ReleaseAudienceResource(http_client)

    def count(
        self,
        *,
        app_id: str,
        bundle_id: str | NotGiven = NOT_GIVEN,
        channel_id: str | NotGiven = NOT_GIVEN,
        git_commit: str | NotGiven = NOT_GIVEN,
        status: Literal["active", "paused", "revoked"] | NotGiven = NOT_GIVEN,
    ) -> Count:
        """The number of the app's releases under the list's filters."""
        return self._http_client.fetch_json(
            "GET",
            resolve_path("/v1/apps/{appId}/releases/count", appId=app_id),
            Count,
            query={
                "bundleId": bundle_id,
                "channelId": channel_id,
                "gitCommit": git_commit,
                "status": status,
            },
        )

    def get(
        self,
        *,
        app_id: str,
        relations: list[ReleaseRelation] | NotGiven = NOT_GIVEN,
        release_id: str,
    ) -> Release:
        """A release with its status: when it went live in the index and when the purge
        completed.
        """
        return self._http_client.fetch_json(
            "GET",
            resolve_path(
                "/v1/apps/{appId}/releases/{releaseId}", appId=app_id, releaseId=release_id
            ),
            Release,
            query={"relations": relations},
        )

    def list(
        self,
        *,
        app_id: str,
        bundle_id: str | NotGiven = NOT_GIVEN,
        channel_id: str | NotGiven = NOT_GIVEN,
        git_commit: str | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        offset: int | NotGiven = NOT_GIVEN,
        relations: list[ReleaseRelation] | NotGiven = NOT_GIVEN,
        status: Literal["active", "paused", "revoked"] | NotGiven = NOT_GIVEN,
    ) -> list[Release]:
        """Every release of the app, newest first; `git_commit` selects those whose bundle's
        commit hash, ref or message contains it.
        """
        return self._http_client.fetch_json(
            "GET",
            resolve_path("/v1/apps/{appId}/releases", appId=app_id),
            list[Release],
            query={
                "bundleId": bundle_id,
                "channelId": channel_id,
                "gitCommit": git_commit,
                "limit": limit,
                "offset": offset,
                "relations": relations,
                "status": status,
            },
        )

    def pause(self, *, app_id: str, release_id: str) -> Release:
        """Stops offering a release; devices on it keep it.

        Pausing a paused release answers it unchanged, so the call is retried.
        """
        return self._http_client.fetch_json(
            "POST",
            resolve_path(
                "/v1/apps/{appId}/releases/{releaseId}/pause", appId=app_id, releaseId=release_id
            ),
            Release,
            is_retryable=True,
        )

    def resume(self, *, app_id: str, release_id: str) -> Release:
        """Offers a paused release again.

        Resuming an active release answers it unchanged, so the call is retried.
        """
        return self._http_client.fetch_json(
            "POST",
            resolve_path(
                "/v1/apps/{appId}/releases/{releaseId}/resume", appId=app_id, releaseId=release_id
            ),
            Release,
            is_retryable=True,
        )

    def revoke(self, *, app_id: str, release_id: str) -> Release:
        """Revokes a release for good: devices on it move to the newest eligible older release or
        the embedded bundle.

        A repeat answers `E_RELEASE_REVOKED`, so the call is never retried.
        """
        return self._http_client.fetch_json(
            "POST",
            resolve_path(
                "/v1/apps/{appId}/releases/{releaseId}/revoke", appId=app_id, releaseId=release_id
            ),
            Release,
        )

    def update(
        self,
        *,
        app_id: str,
        failure_action: FailureAction | None | NotGiven = NOT_GIVEN,
        failure_minimum_update_count: int | None | NotGiven = NOT_GIVEN,
        failure_threshold_percent: int | None | NotGiven = NOT_GIVEN,
        is_mandatory: bool | NotGiven = NOT_GIVEN,
        notes: str | None | NotGiven = NOT_GIVEN,
        progression: ReleaseProgression | None | NotGiven = NOT_GIVEN,
        release_id: str,
        rollout_percentage: int | NotGiven = NOT_GIVEN,
    ) -> Release:
        """Changes the rollout percentage in both directions, the progression schedule, `None`
        stopping it, the mandatory flag, the notes or the auto-pause overrides, `None` inheriting
        the channel's.
        """
        return self._http_client.fetch_json(
            "PATCH",
            resolve_path(
                "/v1/apps/{appId}/releases/{releaseId}", appId=app_id, releaseId=release_id
            ),
            Release,
            body={
                "failureAction": failure_action,
                "failureMinimumUpdateCount": failure_minimum_update_count,
                "failureThresholdPercent": failure_threshold_percent,
                "isMandatory": is_mandatory,
                "notes": notes,
                "progression": progression,
                "rolloutPercentage": rollout_percentage,
            },
        )
