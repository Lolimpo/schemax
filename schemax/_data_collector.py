import re
from dataclasses import dataclass
from typing import Any

from d42.declaration.types import GenericSchema

from ._from_json_schema import _from_json_schema
from ._openapi_normalizer import openapi_normalizer


@dataclass
class SchemaData:
    """Data collector class.

    Attributes:
        http_method: HTTP method of the request.
        path: URL path of the request.
        converted_path: URL path converted to the camel-case for usage in schemax generation.
        args: Arguments of the request.
        queries_schema: Query parameters of the request.
        queries_schema_d42: Converted to d42 queries_schema.
        interface_method: Interface name for usage in schemax generation.
        interface_method_humanized: Interface 'humanized' name for usage in schemax generation.
        status: Status code for specified schemas.
        schema_prefix: Schema prefix name for usage in schemax generation.
        schema_prefix_humanized: Schema prefix 'humanized' name for user in schemax generation.
        response_schema: Normalized response schema (without $ref), None if no schema.
        response_schema_d42: Converted to d42 response_schema, None if no schema.
        request_schema: Normalized request schema (without $ref), None if no schema.
        request_schema_d42: Converted to d42 request_schema, None if no schema.
        request_headers: Request headers from OpenAPI schema.
        request_headers_d42: Converted to d42 request_headers.
        tags: Tags of the request from OpenAPI schema.
    """
    http_method: str
    path: str
    converted_path: str
    args: list[str]
    queries_schema: dict[str, Any]
    queries_schema_d42: GenericSchema
    interface_method: str
    interface_method_humanized: str
    status: str | int
    schema_prefix: str
    schema_prefix_humanized: str
    response_schema: dict[str, Any] | None
    response_schema_d42: GenericSchema | None
    request_schema: dict[str, Any] | None
    request_schema_d42: GenericSchema | None
    request_headers: dict[str, Any]
    request_headers_d42: GenericSchema
    tags: list[str]


humanizator = {
    "get": "Get",
    "post": "Create",
    "put": "Update",
    "patch": "Change",
    "delete": "Delete"
}


def collect_schema_data(value: dict[str, Any]) -> list[SchemaData]:
    normalized_schema = openapi_normalizer(value)
    paths_data = normalized_schema.get("paths", {})

    return [
        schema_data
        for path, path_data in paths_data.items()
        for schema_data in process_paths(path, path_data)
    ]


def process_paths(path: str, path_data: dict[str, Any]) -> list[SchemaData]:
    paths = get_enum_paths(path, path_data)
    if not paths:
        paths = [path]

    schema_data = []
    for enum_path in paths:
        for http_method, method_data in path_data.items():
            if http_method.lower() in ["get", "post", "put", "patch", "delete"]:
                for status in method_data.get("responses", {}):
                    schema_data.append(
                        process_method_data(enum_path, http_method, method_data, int(status))
                    )

    return schema_data


def get_enum_paths(path: str, path_data: dict[str, Any]) -> list[str]:
    paths = []
    parameters = path_data.get("parameters", [])
    for parameter in parameters:
        if parameter.get("in") == "path" and "enum" in parameter["schema"]:
            for enum_item in parameter["schema"]["enum"]:
                paths.append(path.replace(f"{{{parameter['name']}}}", enum_item))
    return paths


def process_method_data(
    path: str, http_method: str, method_data: dict[str, Any], status: int
) -> SchemaData:
    request_schema, response_schema = get_request_response_schemas(method_data, status)
    queries_schema = get_queries(method_data)
    headers_schema = get_headers(method_data)

    args = get_path_arguments(path)
    if request_schema:
        args.append("body")

    queries_schema_d42 = _from_json_schema(queries_schema)
    response_schema_d42 = _from_json_schema(response_schema) if response_schema else None
    request_schema_d42 = _from_json_schema(request_schema) if request_schema else None
    headers_schema_d42 = _from_json_schema(headers_schema)

    return SchemaData(
        http_method=http_method,
        path=path,
        converted_path=convert_to_snake_case(path),
        args=args,
        queries_schema=queries_schema,
        queries_schema_d42=queries_schema_d42,
        interface_method=get_interface_method_name(http_method, path),
        interface_method_humanized=get_interface_method_name(http_method, path, humanized=True),
        status=status,
        schema_prefix=get_schema_prefix(http_method, path),
        schema_prefix_humanized=get_schema_prefix(http_method, path, humanized=True),
        response_schema=response_schema,
        response_schema_d42=response_schema_d42,
        request_schema=request_schema,
        request_schema_d42=request_schema_d42,
        request_headers=headers_schema,
        request_headers_d42=headers_schema_d42,
        tags=method_data.get("tags", [])
    )


def get_request_response_schemas(
    method_data: dict[str, Any], status: int
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    request_schema: dict[str, Any] | None = None
    response_schema: dict[str, Any] | None = None

    if "requestBody" in method_data:
        request_schema = get_request_schema(method_data["requestBody"])
    elif "parameters" in method_data:
        request_schema = get_request_schema_from_parameters(method_data["parameters"])

    if "responses" in method_data:
        response_schema = get_response_schema(method_data["responses"], status)

    return request_schema, response_schema


def get_request_schema(request_body: dict[str, Any]) -> dict[str, Any] | None:
    content = request_body.get("content", {})
    for content_type, content_data in content.items():
        if "schema" in content_data:
            return content_data["schema"]  # type: ignore
    return None


def get_request_schema_from_parameters(parameters: list[dict[str, Any]]) -> dict[str, Any] | None:
    for param in parameters:
        if param["in"] == "body":
            return param["schema"]  # type: ignore
    return None


def get_response_schema(responses: dict[str, Any], need_status: int) -> dict[str, Any] | None:
    for status, status_data in responses.items():
        if int(status) == need_status:
            content = status_data.get("content", {})
            if content:
                content_schema: dict[str, Any] | None = (
                    content.get(next(iter(content)), {}).get("schema", None)
                )
                return content_schema
            schema: dict[str, Any] | None = status_data.get("schema", None)
            if schema:
                return schema
    return None


def get_path_arguments(path: str) -> list[str]:
    return [convert_to_snake_case(arg) for arg in re.findall(r"{([^}]+)}", path)]


def get_queries(method_data: dict[str, Any]) -> dict[str, Any]:
    query_schema = {
        "type": "object",
        "properties": {},
        "required": []
    }

    for parameter in method_data.get("parameters", []):
        if parameter["in"] == "query":
            name = parameter["name"]
            schema = parameter.get("schema", {})
            query_schema["properties"][name] = schema  # type: ignore[index]
            if parameter.get("required", False):
                query_schema["required"].append(name)  # type: ignore[attr-defined]

    if not query_schema["required"]:
        del query_schema["required"]  # Remove list if it's empty

    return query_schema


def get_headers(method_data: dict[str, Any]) -> dict[str, Any]:
    headers_schema = {
        "type": "object",
        "properties": {},
        "required": []
    }

    for parameter in method_data.get("parameters", []):
        if parameter["in"] == "header":
            name = parameter["name"]
            schema = parameter.get("schema", {})
            headers_schema["properties"][name] = schema  # type: ignore[index]
            if parameter.get("required", False):
                headers_schema["required"].append(name)  # type: ignore[attr-defined]

    if not headers_schema["required"]:
        del headers_schema["required"]  # Remove list if it's empty

    return headers_schema


def get_interface_method_name(http_method: str, path: str, humanized: bool = False) -> str:
    return (
        (humanizator[http_method] if humanized else http_method.lower()) +
        "_".join(
            convert_to_snake_case(word)
            .replace("{", "")
            .replace("}", "")
            .replace("-", "_")
            .replace(".", "_")
            .lower()
            for word in path.split("/")
        )
    )


def get_success_status(method_data: dict[str, Any]) -> str | int:
    success_statuses = ["200", 200]
    for status in success_statuses:
        if status in method_data.get("responses", {}):
            return status  # type: ignore
    return ""


def get_schema_prefix(http_method: str, path: str, humanized: bool = False) -> str:
    return (
        (humanizator[http_method] if humanized else http_method.capitalize()) +
        "".join(
            word
            .replace("{", "")
            .replace("}", "")
            .replace("-", "")
            .replace("_", "")
            .replace(".", "")
            .capitalize()
            for word in path.split("/")
        )
    )


def convert_to_snake_case(input_string: str) -> str:
    return re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', input_string).lower()
