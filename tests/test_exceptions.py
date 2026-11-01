import json

import pytest

from hotcodepush import HotCodePushError
from hotcodepush.exceptions import resolve_hot_code_push_error


def test_carries_the_api_error_and_the_status_verbatim_when_the_body_has_the_error_shape() -> None:
    body = json.dumps(
        {
            "code": "validation",
            "details": {"field": "name", "rule": "required"},
            "message": "The name is required.",
        }
    )

    resolved_error = resolve_hot_code_push_error(400, body)

    assert isinstance(resolved_error, HotCodePushError)
    assert resolved_error.code == "validation"
    assert resolved_error.details == {"field": "name", "rule": "required"}
    assert resolved_error.message == str(resolved_error) == "The name is required."
    assert resolved_error.status == 400


@pytest.mark.parametrize(
    "body",
    ["<html>Too Many Requests</html>", '{"error":"Not Found"}'],
    ids=["not_json", "no_shape"],
)
def test_answers_unexpected_response_without_the_body_when_the_body_lacks_the_error_shape(
    body: str,
) -> None:
    resolved_error = resolve_hot_code_push_error(429, body)

    assert resolved_error.code == "unexpected_response"
    assert resolved_error.details is None
    assert resolved_error.message == "Request failed with status 429."
    assert resolved_error.status == 429
