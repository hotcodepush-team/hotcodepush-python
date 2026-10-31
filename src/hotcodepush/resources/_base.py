from __future__ import annotations

from .._http import HttpClient


class BaseResource:
    def __init__(self, http_client: HttpClient) -> None:
        self._http_client = http_client
