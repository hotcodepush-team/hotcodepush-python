# CLAUDE.md

`hotcodepush`, the typed Python client for the HotCodePush REST API, modeled on Capawesome's [`cloud-python`](https://github.com/capawesome-team/cloud-python) and mirroring [`hotcodepush-node`](https://github.com/hotcodepush-team/hotcodepush-node) method for method.
Stack: Python 3.11 or later, httpx (sync) and pydantic v2 at runtime and nothing else; uv for the venv, the lockfile and CI, hatchling for the build, ruff, mypy strict and pytest.

The API contract is planned in the private `handbook` repo, checked out beside this one by maintainers: `../handbook/docs/api.md`, its Conventions and Errors sections above all.
When the code and the contract disagree, stop and surface it; never improvise.
The client is validated against the API's OpenAPI document, the contract; see [The OpenAPI snapshot](#the-openapi-snapshot).

## Layout

```
openapi.json                    the snapshot of the API's OpenAPI document, committed
scripts/sync_openapi.py         fetches the document into openapi.json
scripts/check_openapi_drift.py  fails when the live API's operations differ from openapi.json's, CI's step after the tests
src/hotcodepush/__init__.py     the public exports
src/hotcodepush/client.py       HotCodePush: the options and one attribute per top-level resource
src/hotcodepush/_http.py        the one place that sends a request: the headers, the timeout, send_with_retry, JSON in and out
src/hotcodepush/_upload.py      the single-or-parts rule of an upload
src/hotcodepush/_types.py       NOT_GIVEN, the default of every optional argument
src/hotcodepush/exceptions.py   HotCodePushError and the parsing of the one error shape
src/hotcodepush/models.py       every type a method takes or returns, derived from the snapshot by hand
src/hotcodepush/resources/      one module per resource class
tests/test_<resource>.py        the unit tests of one resource module's methods, through tests/stub_api.py; _upload.py and models.py are tested through them
tests/test_http.py              the unit tests of _http.py and the client's options
tests/test_exceptions.py        the unit tests of exceptions.py
tests/test_openapi.py           the contract test: every resource method against the snapshot
tests/test_integration.py       the client against a running API, skipped unless HOTCODEPUSH_API_BASE_URL is set
tests/stub_api.py               StubApi, the httpx.MockTransport every unit test sends through
tests/openapi_document.py       the snapshot's operations and the examples its schemas describe
```

Resources mirror the paths: `/v1/organizations/{organizationId}/apps` is `organizations.apps`, `/v1/apps/{appId}/channels/{channelId}/releases` is `apps.channels.releases`; a resource nests on the one its path sits under, and a path collection is one class.
The methods are the Node client's, their names in snake_case: `deleteMany` is `delete_many`, `downloadCsv` is `download_csv`.
Module names are the Node file names in snake_case, `channel-releases.ts` being `resources/channel_releases.py`.

Tests stub the transport through `tests/stub_api.py`, answering with the examples `tests/openapi_document.py` derives from the snapshot; nothing calls the real API but the integration test, run by hand.

## Commands

| Command                             | Does                                                      |
| ----------------------------------- | --------------------------------------------------------- |
| `uv sync`                           | the venv from `uv.lock`, the dev tools included           |
| `uv run ruff format .`              | formats the code                                          |
| `uv run ruff format --check .`      | the format check                                          |
| `uv run ruff check .`               | the lint                                                  |
| `uv run mypy`                       | the strict type check of `src`, `tests` and `scripts`     |
| `uv run pytest`                     | the tests, the contract test included                     |
| `uv build`                          | the sdist and the wheel into `dist/`                      |
| `uv run scripts/sync_openapi.py`    | `<HOTCODEPUSH_API_BASE_URL>/openapi` into `openapi.json`  |

Run `uv run ruff format .` before every commit; the format check, lint, type check, tests and build must pass, and CI runs them on Python 3.11 to 3.14 on every pull request and push to `main`, with `uvx twine check dist/*` on the build.
`uv sync --locked` fails when `uv.lock` is stale; commit it with every dependency change.

## The API contract

- Auth is `Authorization: Bearer <token>`; the token falls back to `HOTCODEPUSH_TOKEN` and stays optional, since `/health` needs none.
- Every request sends `X-HotCodePush-Client: <name>/<version>`, `python/<this package's version>` unless the caller passes its own `client`; `User-Agent` goes out only when the caller sets `user_agent`, since a session keeps it and the sessions page names the client by it.
- Every error is one JSON shape, `code`, `message`, `details`; `HotCodePushError` carries them and the status verbatim, and a body without the shape becomes `unexpected_response`.
- Every call goes through `HttpClient`, never a bare `httpx` call: sixty seconds per attempt, `JSON_TIMEOUT_SECONDS` or the caller's `timeout`, and ten minutes for a binary upload, `UPLOAD_TIMEOUT_SECONDS`, each httpx's limit on every phase of the attempt, the connect, each read and write and the pool; `send_with_retry` makes three attempts, backing off exponentially from 500 ms, on a transport error, 408, 429 and 5xx; a 429 or a 503 waits its `Retry-After` instead, at most sixty seconds, the rate-limit window.
- Every creating `POST` — the eight operations whose OpenAPI document lists the `Idempotency-Key` header: organizations, invitations, apps, channels, releases, rollbacks, bundles and binaries — goes through `fetch_creating_post`, which sends the caller's `idempotency_key` or a UUID generated per call and kept across its retries. A checkout and a customer portal session carry no key and are never retried, since each call creates another Polar object.
- Any other `POST` is retried only where a repeat is safe, `is_retryable=True`: `pause`, `resume`, the subscription's `cancel` and `uncancel`, a bundle's `complete`, a channel's bulk `revoke`, a signing key's `create`, the SSO verification, the two multipart starts and a file upload's completion; a pack's completion is never retried, since a repeat answers `not_found` for an upload R2 already closed.
- Lists take `limit` and `offset`; `relations` and `ids` are lists sent as comma lists, `?relations=user`, `?ids=a,b`, and any other list repeats its parameter, `?attribute=a&attribute=b`.
- `me` is accepted wherever a `{userId}` appears; the client passes it through.
- The `/v1/auth/*` slice is Better Auth's and outside the document; its client lives in the CLI and the console, never here.
- Every binary `PUT` goes through `fetch_upload`: the body is `bytes` or a file object with its `content_length`, streamed with `Content-Length` and the documented `Content-Type`; bytes are retried, a file object is read once and never retried.
- An upload's bytes above `SINGLE_UPLOAD_LIMIT_BYTES`, 64 MiB, go up in parts of `PART_SIZE_BYTES`, 10 MiB, numbered from 1, then complete, through `upload_in_parts`; a failed part or completion deletes the upload.

## Resources

- Every argument is keyword-only and snake_case, in alphabetical order; the path parameters are arguments like any other, `app_id=…`.
- An optional argument defaults to `NOT_GIVEN` and is left out of the request; `None` is sent as `null`, so a nullable field is typed `X | None | NotGiven`, any other `X | NotGiven`.
- The body and the query are dicts whose keys are the API's camelCase names, written out, `{"isProtected": is_protected}`, so a name greps against `openapi.json`.
- Every path goes through `resolve_path` with the snapshot's template verbatim, `resolve_path("/v1/apps/{appId}", appId=app_id)`.
- A method returns a model or a list of models, as the API answers; a status-only answer returns `None` through `fetch_status`.
- A model is a `HotCodePushModel` named after the API's entity, its fields the snapshot's properties in snake_case: required ones without a default, nullable ones `X | None`, a relation `X | None = None`; a date-time is a `datetime`, an enum a `Literal`, an alias in `models.py` when two types share it.
- A query flag documented as `"true" | "false"` is a `bool`.
- After a resource's `list` method, an annotation writes `builtins.list`, since the method shadows the builtin in the class body.
- A method whose operation the document marks with `sessionAuth` carries ``An API token answers `forbidden`; sign in with a session.`` in its docstring; the contract test holds the note to the document.

## The OpenAPI snapshot

The API's `/openapi` document is the contract, and `openapi.json` is its committed snapshot, the same bytes as `hotcodepush-node`'s, so the package builds and CI checks without the API.
A schema change breaks `tests/test_openapi.py`, which calls every resource method once with every option it can send and answers it with the example of its operation's documented response: it fails when a method sends a path, method, query parameter, body field or content type the snapshot lacks, when it sends an `Idempotency-Key` where the operation documents none or none where it does, when a response property lands in a model's `model_extra` or fails its validation, when the session note and `sessionAuth` disagree, when a resource method has no call in `CALLS`, and when an operation has no method.

When the API changes:

1. Run the API locally, as `apps/api-worker/README.md` in the monorepo says.
2. `HOTCODEPUSH_API_BASE_URL=http://localhost:8787 uv run scripts/sync_openapi.py`.
3. Fix what no longer passes, and add the resource methods for new endpoints, their models and their calls in `CALLS`.
4. Commit `openapi.json` with the change; it is never edited by hand.

The integration test runs by hand against that API, started with `ENVIRONMENT=dev` and `DEV_DATABASE_URL` in its `.dev.vars` so the mail lands in its log: sign up through `POST /v1/auth/sign-up/email`, send the logged link's token to `GET /v1/auth/verify-email?token=`, sign in through `POST /v1/auth/sign-in/email` and take the `set-auth-token` header, then `HOTCODEPUSH_API_BASE_URL=http://localhost:8787 HOTCODEPUSH_API_TOKEN=<bearer> uv run pytest tests/test_integration.py`.

## Naming

- A name says what the function does on first read: the verb, the object and, where it matters, the qualifier.
- Prefixes: `fetch` for HTTP, `resolve` for derivations without I/O.
- Result variables carry the past participle of their operation: `fetched_channel`, `resolved_error`.
- Alphabetical ordering within a scope: imports, dict keys, keyword arguments, model fields, declarations of one kind.
- Booleans carry `is` or `has`; a state with a moment is a timestamp such as `paused_at`, never a boolean.
- Every value of a catalog is lowercase snake_case with no prefix, error codes included: `not_found`, `unexpected_response`; the API's are passed through verbatim, never renamed.
- Never `cast` or `# type: ignore`; a real check.
- Test titles read `test_<verb>_…`, the verb in the third person, conditions starting with `when`; one test per request and branch.

## Releases

The package has been on PyPI since `0.1.0` and `0.2.0` shipped on 2026-10-25: consumers `pip install hotcodepush` and pin a version, bumping it on purpose.
A release is the merge of release-please's release pull request, never a hand-made tag or upload.
Commits are conventional commits, since release-please reads them; `main` is trunk and CI is the gate.
`.github/workflows/release.yml` runs release-please on every push to `main`: it keeps a release pull request open, and merging it tags the release, builds the distributions and publishes them to PyPI through trusted publishing, with no API token anywhere.
The version lives in `src/hotcodepush/_version.py`, which release-please bumps; the first release is `0.1.0`, the Python strategy's initial version, and `bump-minor-pre-major` with `bump-patch-for-minor-pre-major` keeps every release on `0.x` until `1.0.0` is decided.
A release pull request opened with the workflow's own token starts no CI run; close and reopen it to run the checks.


## Comments

- Comment only what the code cannot say: the why behind a choice, an outside quirk or limit, what a regex matches, a TODO with its issue link. Never what the code does.
- Before adding a comment, try a clearer name or a small extracted function first.
- One or two short plain sentences. Capital letter, full stop, own line above the code. No run-on sentences, no chains of possessives.
- Doc comments (JSDoc, KDoc, `///`, docstrings) only on a package's public API: one line that says what it does, then only what a caller must know.
- Never: section banners, commented-out code, change history, the same comment in two places.

## Agent workspace

- No `.mcp.json` yet: the one server this repo's stack takes is HotCodePush's own, `https://mcp.hotcodepush.com/mcp`, which does not exist yet; it joins the day it does.
- `.claude/skills/` holds the developer skills copied from `hotcodepush-team/.github` with the skills CLI and pinned in `skills-lock.json`; update them with `npx skills update`.
- `.github/copilot-instructions.md` holds the review criteria, the only Copilot-specific file.
