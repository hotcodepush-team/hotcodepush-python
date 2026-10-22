from __future__ import annotations

from .._http import HttpClient


class BaseResource:
    """A resource of the API, sending its requests through the client's one `HttpClient`."""

    def __init__(self, http_client: HttpClient) -> None:
        self._http_client = http_client
