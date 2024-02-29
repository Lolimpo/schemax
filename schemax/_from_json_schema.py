from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

import jsonschema
from district42 import optional
from district42.types import (
    AnySchema,
    BoolSchema,
    DictSchema,
    FloatSchema,
    GenericSchema,
    IntSchema,
    ListSchema,
    NoneSchema,
    StrSchema,
)
from district42_exp_types.unordered import UnorderedSchema

if TYPE_CHECKING:
    import builtins

    EllipsisType = builtins.ellipsis
else:
    EllipsisType = Any


def null_visitor() -> NoneSchema:
    return NoneSchema()


def boolean_visitor(value: Optional[bool] = None) -> BoolSchema:
    if value is None:
        return BoolSchema()
    if value is True:
        return BoolSchema()(True)
    if value is False:
        return BoolSchema()(False)

    return BoolSchema()


def integer_visitor(value: Dict[str, Any]) -> IntSchema:
    sch = IntSchema()

    if "maximum" in value and "minimum" in value:
        if value["minimum"] != value["maximum"]:
            return sch.min(value["minimum"]).max(value["maximum"])
        return sch(value["minimum"])

    if "minimum" in value:
        sch = sch.min(value["minimum"])

    if "maximum" in value:
        sch = sch.max(value["maximum"])

    if "exclusiveMinimum" in value:
        sch = sch.min(value["exclusiveMinimum"] + 1)

    if "exclusiveMaximum" in value:
        sch = sch.max(value["exclusiveMaximum"] - 1)

    return sch


def number_visitor(value: Dict[str, Any]) -> FloatSchema:
    sch = FloatSchema()

    if "maximum" in value and "minimum" in value:
        if value["minimum"] != value["maximum"]:
            return sch.min(value["minimum"]).max(value["maximum"])
        return sch(value["minimum"])

    if "minimum" in value:
        sch = sch.min(value["minimum"])

    if "maximum" in value:
        sch = sch.max(value["maximum"])

    return sch


def string_visitor(value: Dict[str, Any]) -> StrSchema:
    sch = StrSchema()

    if "minLength" in value and "maxLength" in value:
        if value["minLength"] != value["maxLength"]:
            return sch.len(value["minLength"], value["maxLength"])
        return sch.len(value["minLength"])

    if "minLength" in value:
        return sch.len(value["minLength"])

    if "maxLength" in value:
        return sch.len(..., value["maxLength"])

    if "pattern" in value:
        sch = sch.regex(value["pattern"])

    return sch


def array_visitor(value: Dict[str, Any]) -> ListSchema:
    sch = ListSchema()

    if "contains" in value:
        prop = _from_json_schema(value["contains"])
        sch = UnorderedSchema()(prop)

    if "items" in value:
        if not isinstance(value["items"], bool):
            prop = _from_json_schema(value["items"])
            sch = sch(prop)

    if "prefixItems" in value:
        props = [_from_json_schema(item) for item in value["prefixItems"]]

        if value.get("items", True) is True:
            props.append(Ellipsis)  # type: ignore
        sch = sch(props)  # type: ignore

    if "minItems" in value and "maxItems" in value:
        if value["minItems"] != value["maxItems"]:
            return sch.len(value["minItems"], value["maxItems"])
        return sch.len(value["minItems"])

    if "minItems" in value:
        sch = sch.len(value["minItems"])

    if "maxItems" in value:
        sch = sch.len(..., value["maxItems"])

    return sch


def object_visitor(value: Dict[str, Any]) -> DictSchema:
    if "properties" not in value:
        return DictSchema()

    props: Dict[Any, Union[GenericSchema, EllipsisType]] = {}
    for key in value["properties"]:
        if "required" in value:
            if key in value["required"]:
                props[key] = _from_json_schema(value["properties"][key])
            else:
                props[optional(key)] = _from_json_schema(value["properties"][key])
        else:
            props[optional(key)] = _from_json_schema(value["properties"][key])

    if value.get("additionalProperties", True) is True:
        props[Ellipsis] = Ellipsis

    return DictSchema()(props)


def schema_normalize(value: Dict[str, Any]) -> Dict[str, Any]:
    def schema_runner(
        schema: Dict[str, Any], resolver: jsonschema.RefResolver
    ) -> Dict[str, Any]:
        if isinstance(schema, dict):
            if "$ref" in schema:
                with resolver.resolving(schema["$ref"]) as resolved:
                    return schema_runner(resolved, resolver)
            else:
                return {k: schema_runner(v, resolver) for k, v in schema.items()}
        elif isinstance(schema, list):
            return [schema_runner(item, resolver) for item in schema]  # noqa
        else:
            return schema

    ref_resolver = jsonschema.RefResolver("", value)
    return schema_runner(value, ref_resolver)


def _from_json_schema(value: Dict[Any, Any]) -> GenericSchema:
    # Dirty-dirty hack for OApi schemas, need somehow to clarify better
    if "allOf" in value:
        return _from_json_schema(value["allOf"][-1])

    if "enum" in value:
        props: List[GenericSchema] = []
        for var in value["enum"]:
            match type(var).__name__:
                case "NoneType":
                    props.append(NoneSchema())
                case "bool":
                    props.append(BoolSchema()(var))
                case "int":
                    props.append(IntSchema()(var))
                case "float":
                    props.append(FloatSchema()(var))
                case "str":
                    props.append(StrSchema()(var))
                case "list":
                    props.append(ListSchema())
                case "dict":
                    props.append(DictSchema())
        # If we have only one prop type in result we don't need it in AnySchema
        return AnySchema()(*props) if len(props) > 1 else props[0]

    if "type" not in value:
        return AnySchema()

    if isinstance(value["type"], list):
        schemas = []
        for i in value["type"]:
            schemas.append(_from_json_schema({"type": i}))
        if IntSchema() in schemas:
            schemas.append(FloatSchema())
        if FloatSchema() in schemas:
            schemas.append(IntSchema())
        return AnySchema()(*schemas)

    match value["type"]:
        case "null":
            return null_visitor()
        case "boolean":
            return boolean_visitor()
        case "integer":
            return integer_visitor(value)
        case "number":
            return number_visitor(value)
        case "string":
            return string_visitor(value)
        case "array":
            return array_visitor(value)
        case "object":
            return object_visitor(value)
        case _:
            return AnySchema()
