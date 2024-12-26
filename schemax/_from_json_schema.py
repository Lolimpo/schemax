from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from d42 import optional
from d42.declaration.types import (
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


def integer_visitor(value: Dict[str, Any]) -> Union[IntSchema, AnySchema]:
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

    if "nullable" in value:
        if value.get("nullable") is True:
            return AnySchema()(sch, NoneSchema())

    return sch


def number_visitor(value: Dict[str, Any]) -> AnySchema:
    # OpenAPI has two numeric types, number and integer, where number includes both integer and
    # floating-point numbers.
    # https://swagger.io/docs/specification/data-models/data-types/#numbers
    float_sch = FloatSchema()
    int_sch = IntSchema()

    if "maximum" in value and "minimum" in value:
        if value["minimum"] != value["maximum"]:
            return AnySchema()(
                float_sch.min(float(value["minimum"])).max(float(value["maximum"])),
                int_sch.min(int(value["minimum"])).max(int(value["maximum"]))
            )
        return AnySchema()(
            float_sch(float(value["minimum"])), int_sch(int(value["minimum"]))
        )

    if "minimum" in value:
        float_sch = float_sch.min(float(value["minimum"]))
        int_sch = int_sch.min(int(value["minimum"]))

    if "maximum" in value:
        float_sch = float_sch.max(float(value["maximum"]))
        int_sch = int_sch.max(int(value["maximum"]))

    if "nullable" in value:
        if value.get("nullable") is True:
            return AnySchema()(float_sch, int_sch, NoneSchema())

    return AnySchema()(float_sch, int_sch)


def string_visitor(value: Dict[str, Any]) -> Union[StrSchema, AnySchema]:
    sch = StrSchema()

    if "minLength" in value and "maxLength" in value:
        if value["minLength"] == value["maxLength"]:
            return sch.len(value["minLength"])
        return sch.len(value["minLength"], value["maxLength"])

    if "minLength" in value:
        return sch.len(value["minLength"], ...)

    if "maxLength" in value:
        return sch.len(..., value["maxLength"])

    if "pattern" in value:
        sch = sch.regex(value["pattern"])

    if "nullable" in value:
        if value.get("nullable") is True:
            return AnySchema()(sch, NoneSchema())

    return sch


def array_visitor(value: Dict[str, Any]) -> ListSchema:
    sch = ListSchema()

    if "contains" in value:
        prop = _from_json_schema(value["contains"])
        sch = UnorderedSchema()([..., prop, ...])

    if "items" in value:
        if not isinstance(value["items"], bool):
            if "oneOf" in value["items"]:
                props = [_from_json_schema(item) for item in value["items"]["oneOf"]]
                return AnySchema()(*[sch(prop) for prop in props])  # type: ignore
            else:
                prop = _from_json_schema(value["items"])
                sch = sch(prop)

    if "prefixItems" in value:
        props = [_from_json_schema(item) for item in value["prefixItems"]]

        if value.get("items", True) is True:
            props.append(Ellipsis)  # type: ignore
        sch = sch(props)

    if "minItems" in value and "maxItems" in value:
        if value["minItems"] != value["maxItems"]:
            return sch.len(value["minItems"], value["maxItems"])
        return sch.len(value["minItems"])

    if "minItems" in value:
        sch = sch.len(value["minItems"], ...)

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
            # "By default, the properties defined by the properties keyword are not required"
            # https://json-schema.org/understanding-json-schema/reference/object#required
            props[optional(key)] = _from_json_schema(value["properties"][key])

    if value.get("additionalProperties", True) is True:
        props[Ellipsis] = Ellipsis

    return DictSchema()(props)


def _from_json_schema(value: Dict[Any, Any]) -> GenericSchema:
    if "allOf" in value:
        schema: GenericSchema = DictSchema()
        for item in value["allOf"]:
            converted_item = _from_json_schema(item)
            if isinstance(converted_item, DictSchema):
                schema += converted_item
            else:
                schema = converted_item

        # HACK: If ellipsis exists, need to place it at the end of dict schema keys
        if isinstance(schema, DictSchema) and isinstance(schema.props.keys, Dict):
            if schema.props.keys.get(Ellipsis):
                del schema.props.keys[Ellipsis]
                schema = schema.__add__(DictSchema()({Ellipsis: Ellipsis}))
        return schema

    if "oneOf" in value:
        oneof_props: List[GenericSchema] = []
        for var in value["oneOf"]:
            oneof_props.append(_from_json_schema(var))
        # If we have only one prop type in result we don't need it in AnySchema
        return AnySchema()(*oneof_props) if len(oneof_props) else oneof_props[0]

    if "enum" in value:
        enum_props: List[GenericSchema] = []
        for var in value["enum"]:
            match type(var).__name__:
                case "NoneType":
                    enum_props.append(NoneSchema())
                case "bool":
                    enum_props.append(BoolSchema()(var))
                case "int":
                    enum_props.append(IntSchema()(var))
                case "float":
                    enum_props.append(FloatSchema()(var))
                case "str":
                    enum_props.append(StrSchema()(var))
                case "list":
                    enum_props.append(ListSchema())
                case "dict":
                    enum_props.append(DictSchema())
        # If we have only one prop type in result we don't need it in AnySchema
        return AnySchema()(*enum_props) if len(enum_props) > 1 else enum_props[0]

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
