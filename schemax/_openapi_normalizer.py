from typing import Any, Dict, List

from referencing import Registry, Resource
from referencing._core import Resolver

from ._interface import output_warning


def openapi_normalizer(value: Dict[str, Any], max_recursion: int = 5) -> Dict[str, Any]:
    def schema_runner(
        schema: Dict[str, Any], 
        resolver: Resolver[Dict[str, Any]], 
        path: List[str],
        ref_counts: Dict[str, int]
    ) -> Dict[str, Any]:
        if isinstance(schema, dict):
            if "$ref" in schema:
                ref = schema["$ref"]
                ref_counts[ref] = ref_counts.get(ref, 0) + 1
                if ref_counts[ref] > max_recursion:
                    output_warning(f"Recursive reference detected: {ref} (depth: {ref_counts[ref]})")
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
    
    return schema_runner(value, resolver, [], {})
