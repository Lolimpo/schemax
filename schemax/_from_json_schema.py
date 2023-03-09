import re
from curses.ascii import isalpha
from typing import Any, Dict, Union, List

from district42 import optional
from district42.types import (
    BoolSchema,
    DictSchema,
    FloatSchema,
    GenericSchema,
    IntSchema,
    ListSchema,
    NoneSchema,
    StrSchema,
)


def null_visitor() -> NoneSchema:
    return NoneSchema()


def boolean_visitor() -> BoolSchema:
    return BoolSchema()


def integer_visitor(value: Dict[str, Any]) -> IntSchema:
    sch = IntSchema()

    if "maximum" in value and "minimum" in value:
        if value["minimum"] == value["maximum"]:
            return sch(value["minimum"])
        else:
            return sch.min(value["minimum"]).max(value["maximum"])

    if "minimum" in value:
        sch = sch.min(value["minimum"])

    if "maximum" in value:
        sch = sch.max(value["maximum"])

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
        if re.match(r"(\((\S\||\S)+\)\+)+", value["pattern"]):
            sch = sch.alphabet("".join(i for i in value["pattern"] if isalpha(i)))
        else:
            sch = sch.regex(value["pattern"])

    return sch


def array_visitor(value: Dict[str, Any]) -> ListSchema:
    sch = ListSchema()

    if "contains" in value:
        prop = from_json_schema(value["contains"])
        sch = sch(prop)

    if "prefixItems" in value:
        props = [from_json_schema(item) for item in value["prefixItems"]]
        sch = sch(props)

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

    props: Dict[Any, Union[GenericSchema, ellipsis]] = {}
    for key in value["properties"]:
        if "required" in value:
            if key in value["required"]:
                props[key] = from_json_schema(value["properties"][key])
            else:
                props[optional(key)] = from_json_schema(value["properties"][key])
        else:
            props[optional(key)] = from_json_schema(value["properties"][key])
    return DictSchema()(props)


def from_json_schema(value: Dict[Any, Any]) -> GenericSchema:
    if "type" not in value:
        return NoneSchema()

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
            return NoneSchema()
