import json
import os
from pathlib import Path

import httpx

API_BASE_URL = os.environ.get("HOTCODEPUSH_API_BASE_URL", "http://localhost:8787")
SNAPSHOT_PATH = Path(__file__).parent.parent / "openapi.json"
TIMEOUT_SECONDS = 10.0


def sync_openapi() -> None:
    response = httpx.get(f"{API_BASE_URL}/openapi", timeout=TIMEOUT_SECONDS)
    if not response.is_success:
        raise SystemExit(
            f"{API_BASE_URL}/openapi answered {response.status_code}; is the API running?"
        )
    SNAPSHOT_PATH.write_text(
        f"{json.dumps(response.json(), ensure_ascii=False, indent=2)}\n", encoding="utf-8"
    )
    print(f"Wrote the OpenAPI document of {API_BASE_URL} to openapi.json.")


if __name__ == "__main__":
    sync_openapi()
