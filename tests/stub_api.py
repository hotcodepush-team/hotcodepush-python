import json
import re

import httpx

from hotcodepush import HotCodePush
from hotcodepush._http import DEFAULT_BASE_URL, DEFAULT_CLIENT, HttpClient


class StubApi:
    def __init__(self, *responses: httpx.Response) -> None:
        self.http_client = httpx.Client(transport=httpx.MockTransport(self._handle_request))
        self.requests: list[httpx.Request] = []
        self._responses = responses or (httpx.Response(204),)

    @property
    def client(self) -> HotCodePush:
        return HotCodePush(http_client=self.http_client)

    @property
    def last_request(self) -> httpx.Request:
        return self.requests[-1]

    @property
    def sent_methods_and_urls(self) -> list[str]:
        return [f"{request.method} {request.url}" for request in self.requests]

    def create_http_client(self) -> HttpClient:
        return HttpClient(
            base_url=DEFAULT_BASE_URL,
            client=DEFAULT_CLIENT,
            http_client=self.http_client,
            timeout=None,
            token=None,
            user_agent=None,
        )

    def respond(self, request: httpx.Request) -> httpx.Response:
        # The last response repeats once the others are used up.
        response = self._responses[min(len(self.requests), len(self._responses)) - 1]
        return httpx.Response(
            response.status_code, content=response.content, headers=response.headers
        )

    def _handle_request(self, request: httpx.Request) -> httpx.Response:
        request.read()
        self.requests.append(request)
        return self.respond(request)


class MultipartUploadStubApi(StubApi):
    def __init__(self, completed_body: object, failed_part_number: int | None = None) -> None:
        super().__init__()
        self._completed_body = completed_body
        self._failed_part_number = failed_part_number

    def respond(self, request: httpx.Request) -> httpx.Response:
        part_number_match = re.search(r"/parts/(\d+)$", request.url.path)
        part_number = int(part_number_match.group(1)) if part_number_match else None
        if request.method == "DELETE":
            return httpx.Response(
                404, json={"code": "not_found", "message": "The upload does not exist."}
            )
        if request.method == "PUT" and part_number == self._failed_part_number:
            return httpx.Response(
                409, json={"code": "upload_incomplete", "message": "The part was refused."}
            )
        if request.method == "PUT":
            return httpx.Response(
                200, json={"etag": f"etag-{part_number}", "partNumber": part_number}
            )
        if request.url.path.endswith("/complete"):
            return httpx.Response(200, json=self._completed_body)
        return httpx.Response(201, json={"uploadId": "upload"})


def resolve_sent_json(request: httpx.Request) -> object:
    return json.loads(request.content)
