from typing import Any

from referencing import Registry, Resource
from referencing._core import Resolver

from ._interface import output_warning
from ._memoizer import Memoizer, NoopMemoizer


def openapi_normalizer(
    value: dict[str, Any], memoizer: Memoizer | None = None
) -> dict[str, Any]:
    if memoizer is None:
        memoizer = NoopMemoizer()

    recursive_cases: set[str] = set()

    def schema_runner(
        schema: dict[str, Any],
        resolver: Resolver[dict[str, Any]],
        path: list[str],
    ) -> dict[str, Any]:
        if isinstance(schema, dict):
            if "$ref" in schema:
                ref = schema["$ref"]
                if ref in path:
                    recursive_cases.add(f"{ref}")
                    return {}
                memoized_schema = memoizer.get(ref)
                if memoized_schema is not None:
                    return memoized_schema
                resolved = resolver.lookup(schema["$ref"]).contents
                ran_schema = schema_runner(resolved, resolver, path + [ref])
                memoizer.add(ref, ran_schema)
                return ran_schema
            else:
                return {k: schema_runner(v, resolver, path) for k, v in schema.items()}
        elif isinstance(schema, list):
            return [schema_runner(item, resolver, path) for item in schema]
        else:
            return schema

    resource = Resource.opaque(value)
    resolver = Registry().resolver_with_root(resource)
    out_schema = schema_runner(value, resolver, [])

    if recursive_cases:
        warning_output = '\n'.join(recursive_cases)
        output_warning(f"Curicular cases in spec:{warning_output}")
    return out_schema
