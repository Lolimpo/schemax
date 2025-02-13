from typing import Any

from referencing import Registry, Resource
from referencing._core import Resolver

from ._interface import output_warning


def openapi_normalizer(value: dict[str, Any]) -> dict[str, Any]:
    recursive_cases: set[str] = set()
    def schema_runner(
        schema: dict[str, Any],
        resolver: Resolver[dict[str, Any]],
        path: list[str],
        ref_counts: dict[str, int]
    ) -> dict[str, Any]:
        if isinstance(schema, dict):
            if "$ref" in schema:
                ref = schema["$ref"]
                if ref in path:
                    recursive_cases.add(f"{ref}")
                    return {}
                
                resolved = resolver.lookup(schema["$ref"]).contents
                return schema_runner(resolved, resolver, path + [ref], ref_counts)
            else:
                return {k: schema_runner(v, resolver, path, ref_counts) for k, v in schema.items()}
        elif isinstance(schema, list):
            return [schema_runner(item, resolver, path, ref_counts) for item in schema]  # noqa
        else:
            return schema

    resource = Resource.opaque(value)
    resolver = Registry().resolver_with_root(resource)
    out_schema = schema_runner(value, resolver, [], {})

    if recursive_cases:
        output_warning(f"Curicular cases in spec:\n{'\n'.join(recursive_cases)}")
    return out_schema
