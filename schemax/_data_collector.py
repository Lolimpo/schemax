import re
from typing import Any, Dict, List, Tuple, Union

from schemax import from_json_schema

from ._from_json_schema import schema_normalize


def collect_schema_data(value: Dict[str, Any]) -> List[Dict[str, Any]]:
    schema_data: List[Dict[str, Any]] = []
    normalized_schema: Dict[str, Any] = schema_normalize(value)

    if "paths" in normalized_schema:
        for path, path_data in normalized_schema["paths"].items():
            for http_method, method_data in path_data.items():
                request_schema, response_schema = get_request_response_schemas(method_data)

                args = get_path_arguments(path)
                if request_schema:
                    args.append("body")

                tags = method_data.get("tags", [])
                schema_data.append({
                    "http_method": http_method,
                    "path": convert_to_snake_case(path),
                    "args": args,
                    "queries": None,
                    "interface_method": get_interface_method_name(http_method, path),
                    "status": get_success_status(method_data),
                    "schema_prefix": get_schema_prefix(http_method, path),
                    "response_schema": from_json_schema(response_schema),
                    "request_schema": from_json_schema(request_schema),
                    "tags": tags
                })

    return schema_data


def get_request_response_schemas(
    method_data: Dict[str, Any]
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    request_schema: Dict[str, Any] = {}
    response_schema: Dict[str, Any] = {}

    if "requestBody" in method_data:
        request_schema = get_request_schema(method_data["requestBody"])
    elif "parameters" in method_data:
        request_schema = get_request_schema_from_parameters(method_data["parameters"])

    if "responses" in method_data:
        response_schema = get_response_schema(method_data["responses"])

    return request_schema, response_schema


def get_request_schema(request_body: Dict[str, Any]) -> Dict[str, Any]:
    content = request_body.get("content", {})
    json_content = content.get("application/json", {}).get("schema", {})
    return json_content  # type: ignore


def get_request_schema_from_parameters(parameters: List[Dict[str, Any]]) -> Dict[str, Any]:
    for param in parameters:
        if param["in"] == "body":
            return param["schema"]  # type: ignore
    return {}


def get_response_schema(responses: Dict[str, Any]) -> Dict[str, Any]:
    for status, status_data in responses.items():
        if status == "200" or status == 200:  # type: ignore
            content = status_data.get("content", {})
            content_schema: Dict[str, Any] = content.get(next(iter(content)), {}).get("schema", {})
            return content_schema
    return {}


def get_path_arguments(path: str) -> List[str]:
    return [convert_to_snake_case(arg) for arg in re.findall(r"{([^}]+)}", path)]


def get_interface_method_name(http_method: str, path: str) -> str:
    return (
        http_method.lower() +
        "_".join(
            convert_to_snake_case(word)
            .replace("{", "")
            .replace("}", "")
            .replace("-", "_")
            .lower()
            for word in path.split("/")
        )
    )


def get_success_status(method_data: Dict[str, Any]) -> Union[str, int]:
    success_statuses = ["200", 200]
    for status in success_statuses:
        if status in method_data.get("responses", {}):
            return status  # type: ignore
    return ""


def get_schema_prefix(http_method: str, path: str) -> str:
    return (
        http_method.capitalize() +
        "".join(
            word
            .replace("{", "")
            .replace("}", "")
            .replace("-", "")
            .capitalize()
            for word in path.split("/")
        )
    )


def convert_to_snake_case(input_string: str) -> str:
    return re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', input_string).lower()
