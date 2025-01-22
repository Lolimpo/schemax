from typing import Any, Dict, List

from referencing import Registry, Resource
from referencing._core import Resolver


def openapi_normalizer(value: Dict[str, Any]) -> Dict[str, Any]:
    def schema_runner(
        schema: Dict[str, Any], resolver: Resolver[Dict[str, Any]], path: List[str]
    ) -> Dict[str, Any]:
        if isinstance(schema, dict):
            if "$ref" in schema:
                ref = schema["$ref"]
                if ref in path:
                    raise RuntimeError(f"Circular reference detected: {' -> '.join(path + [ref])}")
                resolved = resolver.lookup(schema["$ref"]).contents
                return schema_runner(resolved, resolver, path + [ref])
            else:
                return {k: schema_runner(v, resolver, path) for k, v in schema.items()}
        elif isinstance(schema, list):
            return [schema_runner(item, resolver, path) for item in schema]  # noqa
        else:
            return schema

    resource = Resource.opaque(value)
    resolver = Registry().resolver_with_root(resource)

    return schema_runner(value, resolver, [])
