# hotcodepush

[![PyPI](https://img.shields.io/pypi/v/hotcodepush)](https://pypi.org/project/hotcodepush/)

The typed Python client for the [HotCodePush](https://hotcodepush.com) REST API, the over-the-air (OTA) update platform for React Native, Expo, Capacitor and Cordova.

## Installation

```sh
pip install hotcodepush
```

Or with uv:

```sh
uv add hotcodepush
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
Every method takes keyword arguments and returns pydantic models with snake_case fields.
An optional argument you leave out stays out of the request; `None` sends `null`, which clears a field such as a channel's `expires_at`.
`users.get(user_id="me")` answers the caller behind the token, as `me` addresses the caller wherever the API takes a `{userId}`.

An upload takes `bytes` or a file object with its `content_length`, and streams it.
Bytes above 64 MiB go up in parts, and a retry sends them again; a file object is read once, so a failed upload of one is not retried.

Creating an organization, an invitation, an app, a channel, a release, a rollback, a bundle or a binary sends an `Idempotency-Key`, a UUID per call kept across the client's own retries; pass `idempotency_key` to reuse one when you retry the call yourself, and the API answers the first result again for 24 hours.

A failed request raises a `HotCodePushError` with the API's `code`, `message` and `details` and the HTTP `status`.

## Documentation

The documentation lives at [hotcodepush.com/docs/api/python](https://hotcodepush.com/docs/api/python).

## Development

```sh
uv sync
uv run ruff format --check .
uv run ruff check .
uv run mypy
uv run pytest
uv build
```

`uv run ruff format .` formats the code.

## License

See [LICENSE](./LICENSE).
