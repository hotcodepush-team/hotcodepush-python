from __future__ import annotations

from datetime import datetime
from typing import Literal

from .._http import resolve_path
from .._types import NOT_GIVEN, NotGiven
from ..models import AuditLog, AuditLogRelation, Count
from ._base import BaseResource


class AuditLogsResource(BaseResource):
    def count(
        self,
        *,
        actor_type: Literal["system", "user"] | NotGiven = NOT_GIVEN,
        app_id: str | NotGiven = NOT_GIVEN,
        created_since: datetime | NotGiven = NOT_GIVEN,
        created_until: datetime | NotGiven = NOT_GIVEN,
        organization_id: str,
        type: str | NotGiven = NOT_GIVEN,
        user_id: str | NotGiven = NOT_GIVEN,
    ) -> Count:
        """The number of the audit log's rows under the list's filters.

        An API token answers `forbidden`; sign in with a session.
        """
        return self._http_client.fetch_json(
            "GET",
            resolve_path(
                "/v1/organizations/{organizationId}/audit-logs/count",
                organizationId=organization_id,
            ),
            Count,
            query={
                "actorType": actor_type,
                "appId": app_id,
                "createdSince": created_since,
                "createdUntil": created_until,
                "type": type,
                "userId": user_id,
            },
        )

    def download_csv(
        self,
        *,
        actor_type: Literal["system", "user"] | NotGiven = NOT_GIVEN,
        app_id: str | NotGiven = NOT_GIVEN,
        created_since: datetime | NotGiven = NOT_GIVEN,
        created_until: datetime | NotGiven = NOT_GIVEN,
        organization_id: str,
        type: str | NotGiven = NOT_GIVEN,
        user_id: str | NotGiven = NOT_GIVEN,
    ) -> bytes:
        """The audit log under the list's filters as `text/csv`, every matching row, read whole.

        An API token answers `forbidden`; sign in with a session.
        """
        return self._http_client.fetch_bytes(
            "GET",
            resolve_path(
                "/v1/organizations/{organizationId}/audit-logs", organizationId=organization_id
            ),
            query={
                "actorType": actor_type,
                "appId": app_id,
                "createdSince": created_since,
                "createdUntil": created_until,
                "format": "csv",
                "type": type,
                "userId": user_id,
            },
        )

    def list(
        self,
        *,
        actor_type: Literal["system", "user"] | NotGiven = NOT_GIVEN,
        app_id: str | NotGiven = NOT_GIVEN,
        created_since: datetime | NotGiven = NOT_GIVEN,
        created_until: datetime | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        offset: int | NotGiven = NOT_GIVEN,
        organization_id: str,
        relations: list[AuditLogRelation] | NotGiven = NOT_GIVEN,
        type: str | NotGiven = NOT_GIVEN,
        user_id: str | NotGiven = NOT_GIVEN,
    ) -> list[AuditLog]:
        """The organization's audit log, newest first, on a plan that includes it, `plan_required`
        otherwise; `type` takes `channel.*` for every action on an object.

        An API token answers `forbidden`; sign in with a session.
        """
        return self._http_client.fetch_json(
            "GET",
            resolve_path(
                "/v1/organizations/{organizationId}/audit-logs", organizationId=organization_id
            ),
            list[AuditLog],
            query={
                "actorType": actor_type,
                "appId": app_id,
                "createdSince": created_since,
                "createdUntil": created_until,
                "limit": limit,
                "offset": offset,
                "relations": relations,
                "type": type,
                "userId": user_id,
            },
        )
