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
    branches: list[dict[str, Any]] = schema.get("anyOf") or schema.get("oneOf") or [schema]
    return branches


def resolve_documented_operation_names() -> set[str]:
    return {
        f"{method.upper()} {template}"
        for template, path_item in OPENAPI_DOCUMENT["paths"].items()
        for method in path_item
        if method in HTTP_METHODS
    }


def resolve_object_example(schema: dict[str, Any]) -> dict[str, object]:
    example = {
        name: resolve_schema_example(property_schema)
        for name, property_schema in schema.get("properties", {}).items()
    }
    value_schema = schema.get("additionalProperties")
    # An empty schema allows any value and adds no entry.
    if isinstance(value_schema, dict) and value_schema:
        names = schema.get("propertyNames", {}).get("enum", ["key"])
        example |= {name: resolve_schema_example(value_schema) for name in names}
    return example


def resolve_operation(method: str, template: str) -> dict[str, Any]:
    operation: dict[str, Any] = OPENAPI_DOCUMENT["paths"][template][method.lower()]
    return operation


def resolve_path_template(path: str) -> str | None:
    return next(
        (
            template
            for template in OPENAPI_DOCUMENT["paths"]
            if re.fullmatch(re.sub(r"\{\w+\}", "[^/]+", template), path)
        ),
        None,
    )


def resolve_response_example(method: str, template: str) -> object:
    responses = resolve_operation(method, template)["responses"]
    schema = next(
        response["content"]["application/json"]["schema"]
        for status, response in responses.items()
        if status.startswith("2") and "application/json" in response.get("content", {})
    )
    return resolve_schema_example(schema)


def resolve_schema_example(schema: dict[str, Any]) -> object:
    branches = [branch for branch in resolve_branches(schema) if branch.get("type") != "null"]
    if branches != [schema]:
        return resolve_schema_example(branches[0])
    if "const" in schema:
        return schema["const"]
    if "enum" in schema:
        return schema["enum"][0]
    schema_type = resolve_schema_type(schema)
    if schema_type == "object":
        return resolve_object_example(schema)
    if schema_type == "array":
        return [resolve_schema_example(branch) for branch in resolve_branches(schema["items"])]
    if schema_type == "string":
        return EXAMPLE_STRINGS_BY_FORMAT.get(schema.get("format", ""), "string")
    if schema_type == "integer":
        return 1
    if schema_type == "boolean":
        return True
    raise ValueError(f"The schema {schema} has no example.")


def resolve_schema_type(schema: dict[str, Any]) -> object:
    schema_type = schema.get("type")
    if isinstance(schema_type, list):
        return next(item for item in schema_type if item != "null")
    return schema_type
