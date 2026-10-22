import json

from hotcodepush import HotCodePushError
from hotcodepush.exceptions import resolve_hot_code_push_error


def test_carries_the_api_error_and_the_status_verbatim_when_the_body_has_the_error_shape() -> None:
    body = json.dumps(
        {
            "code": "E_VALIDATION",
            "details": {"field": "name", "rule": "required"},
            "message": "The name is required.",
        }
    )

    resolved_error = resolve_hot_code_push_error(400, body)

    assert isinstance(resolved_error, HotCodePushError)
    assert resolved_error.code == "E_VALIDATION"
    assert resolved_error.details == {"field": "name", "rule": "required"}
    assert resolved_error.message == str(resolved_error) == "The name is required."
    assert resolved_error.status == 400


def test_answers_e_unexpected_response_without_the_body_when_the_body_is_html() -> None:
    resolved_error = resolve_hot_code_push_error(429, "<html>Too Many Requests</html>")

    assert resolved_error.code == "E_UNEXPECTED_RESPONSE"
    assert resolved_error.details is None
    assert resolved_error.message == "Request failed with status 429."
    assert resolved_error.status == 429


def test_answers_e_unexpected_response_with_the_status_when_the_body_is_plain_text() -> None:
    resolved_error = resolve_hot_code_push_error(503, "unavailable")

    assert (resolved_error.code, resolved_error.status) == ("E_UNEXPECTED_RESPONSE", 503)


def test_answers_e_unexpected_response_when_the_json_lacks_the_error_shape() -> None:
    resolved_error = resolve_hot_code_push_error(404, '{"error":"Not Found"}')

    assert (resolved_error.code, resolved_error.status) == ("E_UNEXPECTED_RESPONSE", 404)
