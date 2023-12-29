# flake8: noqa
import re
from typing import Any, Dict, List

from schemax import from_json_schema

from ._from_json_schema import schema_normalize


# TODO: Need to refactor completely that method, making it more readable, divide into different
def collect_schema_data(value: Dict[str, Any]) -> List[Dict[str, Any]]:
    schema_data: List[Dict[str, Any]] = []

    normalized_schema: Dict[str, Any] = schema_normalize(value)

    if "paths" in normalized_schema:
        for path in normalized_schema["paths"]:
            for http_method in normalized_schema["paths"][path]:
                request_schema: Dict[str, Any] = {}
                response_schema: Dict[str, Any] = {}
                args: List[str] = []
                tags: List[str] = []

                schema_prefix: str = http_method.capitalize() + \
                    "".join(word.replace("{", "").replace("}", "").replace("-", "").capitalize()
                            for word in path.split("/"))

                interface_method: str = http_method.lower() + \
                    "_".join(word.replace("{", "").replace("}", "").replace("-", "").lower()
                            for word in path.split("/"))

                if "{" in path:
                    args = re.findall(r"{([^}]+)}", path)

                if http_method.lower() == "post":
                    args.append("body")

                if "tags" in normalized_schema["paths"][path][http_method]:
                    tags = normalized_schema["paths"][path][http_method]["tags"]

                if "requestBody" in normalized_schema["paths"][path][http_method]:
                    if "content" in normalized_schema["paths"][path][http_method]["requestBody"]:
                        if "application/json" in normalized_schema["paths"][path][http_method]["requestBody"]["content"]:
                            request_schema = normalized_schema["paths"][path][http_method]["requestBody"]["content"]["application/json"]["schema"]
                elif "parameters" in normalized_schema["paths"][path][http_method]:
                    for params in normalized_schema["paths"][path][http_method]["parameters"]:
                        if params["in"] == "body":
                            request_schema = params["schema"]

                if "responses" in normalized_schema["paths"][path][http_method]:
                    for status in normalized_schema["paths"][path][http_method]["responses"]:
                        if status == "200":
                            if "content" in normalized_schema["paths"][path][http_method]["responses"][status]:
                                if "application/json" in normalized_schema["paths"][path][http_method]["responses"][status]["content"]:
                                    response_schema = normalized_schema["paths"][path][http_method]["responses"][status]["content"]["application/json"]["schema"]
                            elif "schema" in normalized_schema["paths"][path][http_method]["responses"][status]:
                                response_schema = normalized_schema["paths"][path][http_method]["responses"][status]["schema"]

                            schema_data.append({
                                "http_method": http_method,
                                "path": path,
                                "args": args,
                                "interface_method": interface_method,
                                "status": status,
                                "schema_prefix": schema_prefix,
                                "response_schema": from_json_schema(response_schema),
                                "request_schema": from_json_schema(request_schema),
                                "tags": tags
                            })

    return schema_data
