import re
from curses.ascii import isalpha
from typing import Any

from district42.types import (
    BoolSchema,
    BytesSchema,
    DictSchema,
    FloatSchema,
    GenericSchema,
    IntSchema,
    ListSchema,
    NoneSchema,
    StrSchema,
)


def from_json_schema(value: Any) -> GenericSchema:
    if "type" in value:
        match value["type"]:
            case "null":
                return NoneSchema()
            case "boolean":
                return BoolSchema()
            case "integer":
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
            case "number":
                sch = FloatSchema()
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
            case "string":
                sch = StrSchema()
                if "minLength" in value and "maxLength" in value:
                    if value["minLength"] == value["maxLength"]:
                        return sch.len(value["minLength"])
                    else:
                        return sch.len(value["minLength"], value["maxLength"])
                if "minLength" in value:
                    return sch.len(value["minLength"])
                if "maxLength" in value:
                    return sch.len(..., value["maxLength"])
                if "pattern" in value:
                    if re.search(r"(\((\S\||\S)+\)\+)+", value["pattern"]):
                        sch = sch.alphabet("".join(i for i in value["pattern"] if isalpha(i)))
                    else:
                        sch = sch.regex(value["pattern"])
                return sch
            case "array":
                sch = ListSchema()
                if "minItems" in value and "maxItems" in value:
                    if value["minItems"] == value["maxItems"]:
                        return sch.len(value["minItems"])
                    else:
                        return sch.len(value["minItems"], value["maxItems"])
                if "minItems" in value:
                    sch = sch.len(value["minItems"])
                if "maxItems" in value:
                    sch = sch.len(..., value["maxItems"])
                return sch
            case "object":
                if "properties" in value:
                    sch = {}
                    for key in value["properties"]:
                        sch[key] = from_json_schema(value["properties"][key])
                    return DictSchema()(sch)
                return DictSchema()
