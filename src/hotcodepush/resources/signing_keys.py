from __future__ import annotations

from .._http import resolve_path
from .._types import NOT_GIVEN, NotGiven
from ..models import Count, SigningKey
from ._base import BaseResource


class SigningKeysResource(BaseResource):
    def count(self, *, app_id: str) -> Count:
        """The number of the app's signing keys."""
        return self._http_client.fetch_json(
            "GET", resolve_path("/v1/apps/{appId}/signing-keys/count", appId=app_id), Count
        )

    def create(self, *, app_id: str, public_key: str) -> SigningKey:
        """Registers a public key, `rsa-v1_5-sha256:` and the base64 of an RSA key's SPKI DER, of
        at least 2048 bits; from then on the app releases only signed bundles.

        A key the app already holds answers its row unchanged, so the call is retried.
        """
        return self._http_client.fetch_json(
            "POST",
            resolve_path("/v1/apps/{appId}/signing-keys", appId=app_id),
            SigningKey,
            body={"publicKey": public_key},
            is_retryable=True,
        )

    def delete(self, *, app_id: str, signing_key_id: str) -> None:
        self._http_client.fetch_status(
            "DELETE",
            resolve_path(
                "/v1/apps/{appId}/signing-keys/{signingKeyId}",
                appId=app_id,
                signingKeyId=signing_key_id,
            ),
        )

    def list(
        self,
        *,
        app_id: str,
        limit: int | NotGiven = NOT_GIVEN,
        offset: int | NotGiven = NOT_GIVEN,
    ) -> list[SigningKey]:
        """The app's signing keys, newest first."""
        return self._http_client.fetch_json(
            "GET",
            resolve_path("/v1/apps/{appId}/signing-keys", appId=app_id),
            list[SigningKey],
            query={"limit": limit, "offset": offset},
        )
