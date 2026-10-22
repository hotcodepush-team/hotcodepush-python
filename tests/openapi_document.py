"""The OpenAPI snapshot, its operations and the examples its schemas describe."""

import json
import re
from pathlib import Path
from typing import Any

OPENAPI_DOCUMENT: dict[str, Any] = json.loads(
    (Path(__file__).parent.parent / "openapi.json").read_text()
)
EXAMPLE_STRINGS_BY_FORMAT = {
    "date": "2026-10-01",
    "date-time": "2026-10-01T12:00:00.000Z",
    "uuid": "00000000-0000-4000-8000-000000000000",
}
HTTP_METHODS = ("delete", "get", "patch", "post", "put")


def resolve_branches(schema: dict[str, Any]) -> list[dict[str, Any]]:
    """The branches of a union, `anyOf` or `oneOf`, or the schema itself."""
    branches: list[dict[str, Any]] = schema.get("anyOf") or schema.get("oneOf") or [schema]
    return branches


def resolve_documented_operation_names() -> set[str]:
    return {
        f"{method.upper()} {template}"
        for template, path_item in OPENAPI_DOCUMENT["paths"].items()
        for method in path_item
        if method in HTTP_METHODS
    }


def resolve_operation(method: str, template: str) -> dict[str, Any]:
    operation: dict[str, Any] = OPENAPI_DOCUMENT["paths"][template][method.lower()]
    return operation


def resolve_path_template(path: str) -> str | None:
    """The template of the snapshot a concrete path fills, `/v1/apps/{appId}` for `/v1/apps/a`."""
    return next(
        (
            template
            for template in OPENAPI_DOCUMENT["paths"]
            if re.fullmatch(re.sub(r"\{\w+\}", "[^/]+", template), path)
        ),
        None,
    )


def resolve_response_example(method: str, template: str) -> object:
    """The body the operation's 2xx JSON response schema describes, every property set."""
    responses = resolve_operation(method, template)["responses"]
    schema = next(
        response["content"]["application/json"]["schema"]
        for status, response in responses.items()
        if status.startswith("2") and "application/json" in response.get("content", {})
    )
    return resolve_schema_example(schema)


def resolve_schema_example(schema: dict[str, Any]) -> object:
    """A value of the schema with every property set: the first branch of a union but `null`,
    the first value of an enum, and an array of one item per branch of its items' union.
    """
    branches = [branch for branch in resolve_branches(schema) if branch.get("type") != "null"]
    if branches != [schema]:
        return resolve_schema_example(branches[0])
    if "const" in schema:
        return schema["const"]
    if "enum" in schema:
        return schema["enum"][0]
    schema_type = schema.get("type")
    if isinstance(schema_type, list):
        schema_type = next(item for item in schema_type if item != "null")
    if schema_type == "object":
        return {
            name: resolve_schema_example(property_schema)
            for name, property_schema in schema.get("properties", {}).items()
        }
    if schema_type == "array":
        return [resolve_schema_example(branch) for branch in resolve_branches(schema["items"])]
    if schema_type == "string":
        return EXAMPLE_STRINGS_BY_FORMAT.get(schema.get("format", ""), "string")
    if schema_type == "integer":
        return 1
    if schema_type == "boolean":
        return True
    raise ValueError(f"The schema {schema} has no example.")
