from __future__ import annotations

from typing import Literal

from .._http import resolve_path
from .._types import NOT_GIVEN, NotGiven
from ._base import BaseResource


class QrCodesResource(BaseResource):
    def get(
        self,
        *,
        format: Literal["png", "svg"] | NotGiven = NOT_GIVEN,
        size: int | NotGiven = NOT_GIVEN,
        url: str,
    ) -> bytes:
        """Gets `url` as a QR image, SVG unless `format` is `png`, `size` pixels wide.

        The URL must be on hotcodepush.com or one of its subdomains, otherwise the API answers
        `validation` with the rule `host_not_allowed`. Needs no token.
        """
        return self._http_client.fetch_bytes(
            "GET",
            resolve_path("/v1/qr-codes"),
            query={"format": format, "size": size, "url": url},
        )
