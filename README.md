# hotcodepush

[![PyPI](https://img.shields.io/pypi/v/hotcodepush)](https://pypi.org/project/hotcodepush/)

The typed Python client for the [HotCodePush](https://hotcodepush.com) REST API, the over-the-air (OTA) update platform for React Native, Expo, Capacitor and Cordova.

## Installation

```sh
pip install hotcodepush    # or: uv add hotcodepush
```

It requires Python 3.11 or later.

## Usage

```python
from hotcodepush import HotCodePush

hot_code_push = HotCodePush()  # reads the API token from HOTCODEPUSH_TOKEN

organization, *_ = hot_code_push.organizations.list()
app = hot_code_push.organizations.apps.create(
    framework="capacitor", name="Demo", organization_id=organization.id
)
channel = hot_code_push.apps.channels.create(app_id=app.id, name="staging")
hot_code_push.apps.channels.pause(app_id=app.id, channel_id=channel.id)
```

The resources mirror the API's paths, `/v1/apps/{appId}/channels` being `apps.channels`.
Every method takes keyword arguments and returns pydantic models with snake_case fields; an argument left out stays out of the request, and `None` sends `null`.
Uploads take `bytes` or a file object with its `content_length` and stream it.
Creating calls send an `Idempotency-Key` and are retried; pass `idempotency_key` to reuse one across your own retries.
A failed request raises a `HotCodePushError` with the API's `code`, `message`, `details` and the HTTP `status`; `code` is a `str`, so a code newer than your client passes through, and `ErrorCode` lists the codes this version knows.

## Documentation

See [hotcodepush.com/docs/api/python](https://hotcodepush.com/docs/api/python).

## Development

```sh
uv sync
uv run pytest
uv run ruff check . && uv run mypy
uv run ruff format .       # run before every commit
uv build
```

`uv run scripts/sync_openapi.py` fetches the API's OpenAPI document into `openapi.json`, which the contract test checks the client against.
`CLAUDE.md` holds the layout and the rules.

## License

See [LICENSE](./LICENSE).
