import json
import sys
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

LIVE_DOCUMENT_URL = "https://api.hotcodepush.com/openapi"
SNAPSHOT_PATH = Path(__file__).parent.parent / "openapi.json"
HTTP_METHODS = ("delete", "get", "patch", "post", "put")
TIMEOUT_SECONDS = 10.0
# The edge refuses urllib's default User-Agent with a 403.
USER_AGENT = "hotcodepush-python/check_openapi_drift"


def check_openapi_drift() -> None:
    try:
        live_document = fetch_live_document()
    except (TimeoutError, URLError) as error:
        if isinstance(error, HTTPError) and error.code < 500:
            raise
        print(f"Skipped the drift check: {LIVE_DOCUMENT_URL} is unreachable ({error}).")
        return
    snapshot_document = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
    live_operations = resolve_operation_names(live_document)
    snapshot_operations = resolve_operation_names(snapshot_document)
    if live_operations == snapshot_operations:
        print(f"openapi.json documents the operations of {LIVE_DOCUMENT_URL}.")
        return
    for operation in sorted(live_operations - snapshot_operations):
        print(f"Only live: {operation}")
    for operation in sorted(snapshot_operations - live_operations):
        print(f"Only in openapi.json: {operation}")
    sys.exit(f"openapi.json has drifted from {LIVE_DOCUMENT_URL}; sync it as CLAUDE.md says.")


def fetch_live_document() -> Any:
    request = Request(LIVE_DOCUMENT_URL, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
        return json.load(response)


def resolve_operation_names(document: Any) -> set[str]:
    return {
        f"{method.upper()} {template}"
        for template, path_item in document["paths"].items()
        for method in path_item
        if method in HTTP_METHODS
    }


if __name__ == "__main__":
    check_openapi_drift()
