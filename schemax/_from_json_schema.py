from typing import TYPE_CHECKING, Any, Dict, Optional, Union

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
        prop = from_json_schema(value["contains"])
        sch = UnorderedSchema()(prop)

    if "items" in value:
        if not isinstance(value["items"], bool):
            prop = from_json_schema(value["items"])
            sch = sch(prop)

    if "prefixItems" in value:
        props = [from_json_schema(item) for item in value["prefixItems"]]

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
                props[key] = from_json_schema(value["properties"][key])
            else:
                props[optional(key)] = from_json_schema(value["properties"][key])
        else:
            props[optional(key)] = from_json_schema(value["properties"][key])

    if value.get("additionalProperties", True) is True:
        props[Ellipsis] = Ellipsis

    return DictSchema()(props)


def from_json_schema(value: Dict[Any, Any]) -> GenericSchema:
    if "enum" in value:
        if len(value["enum"]) > 1:
            return AnySchema()
        return boolean_visitor(*value["enum"])

    if "type" not in value:
        return AnySchema()

    if isinstance(value["type"], list):
        schemas = []
        for i in value["type"]:
            schemas.append(from_json_schema({"type": i}))
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
