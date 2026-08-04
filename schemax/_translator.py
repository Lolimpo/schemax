import re
import warnings
from typing import Any

from d42.declaration import SchemaVisitor
from d42.declaration.types import (
    AnySchema,
    BoolSchema,
    BytesSchema,
    DateSchema,
    DateTimeSchema,
    DictSchema,
    FloatSchema,
    GenericTypeAliasSchema,
    IntSchema,
    ListSchema,
    NoneSchema,
    StrSchema,
    TypeAliasPropsType,
    UUID4Schema,
)
from d42.utils import is_ellipsis
from niltype import Nil

from schemax import supported_props

_UUID_LOWERCASE_PATTERN = (
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
)
_UUID_UPPERCASE_PATTERN = (
    r"^[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}$"
)


class Translator(SchemaVisitor[Any]):
    def visit_none(self, schema: NoneSchema, **kwargs: Any) -> dict[str, Any]:
        return {"type": "null"}

    def visit_bool(self, schema: BoolSchema, **kwargs: Any) -> dict[str, Any]:
        for prop in schema.props:
            if prop not in supported_props.BoolProps:
                warnings.warn(f"Unsupported prop {prop} for type {schema.__str__()}", Warning)

        if schema.props.value is Nil:
            return {"type": "boolean"}

        return {"enum": [schema.props.value]}

    def visit_int(self, schema: IntSchema, **kwargs: Any) -> dict[str, Any]:
        for prop in schema.props:
            if prop not in supported_props.IntProps:
                warnings.warn(f"Unsupported prop {prop} for type {schema.__str__()}", Warning)

        int_object: dict[str, Any] = {
            "type": "integer"
        }

        if schema.props.value is not Nil:
            int_object["minimum"] = schema.props.value
            int_object["maximum"] = schema.props.value

        if schema.props.min is not Nil:
            int_object["minimum"] = schema.props.min
        if schema.props.max is not Nil:
            int_object["maximum"] = schema.props.max

        return int_object

    def visit_float(self, schema: FloatSchema, **kwargs: Any) -> dict[str, Any]:
        for prop in schema.props:
            if prop not in supported_props.FloatProps:
                warnings.warn(f"Unsupported prop {prop} for type {schema.__str__()}", Warning)

        number_object: dict[str, Any] = {
            "type": "number"
        }

        if schema.props.value is not Nil:
            number_object["minimum"] = schema.props.value
            number_object["maximum"] = schema.props.value

        if schema.props.min is not Nil:
            number_object["minimum"] = schema.props.min
        if schema.props.max is not Nil:
            number_object["maximum"] = schema.props.max

        if schema.props.precision is not Nil:
            number_object["multipleOf"] = 10 ** -schema.props.precision

        return number_object

    def visit_str(self, schema: StrSchema, **kwargs: Any) -> dict[str, Any]:
        for prop in schema.props:
            if prop not in supported_props.StrProps:
                warnings.warn(f"Unsupported prop {prop} for type {schema.__str__()}", Warning)

        str_object: dict[str, Any] = {
            "type": "string"
        }

        if schema.props.value is not Nil:
            str_object["const"] = schema.props.value

        if schema.props.pattern is not Nil:
            if re.search(r"\\\w", schema.props.pattern) is not None:
                warnings.warn("Be aware that escape-sequences are unsupported in json-schemas "
                              "regexes. Currently we can't do reformation and provide them "
                              "'as it is'.\nUse at our own risk!", Warning)
            str_object["pattern"] = schema.props.pattern

        if schema.props.len is not Nil:
            str_object["minLength"] = schema.props.len
            str_object["maxLength"] = schema.props.len

        if schema.props.min_len is not Nil:
            str_object["minLength"] = schema.props.min_len
        if schema.props.max_len is not Nil:
            str_object["maxLength"] = schema.props.max_len

        if schema.props.alphabet is not Nil:
            str_object["pattern"] = "^(" \
                                    + "|".join(re.escape(a) for a in schema.props.alphabet) \
                                    + ")+$"

        if schema.props.substr is not Nil:
            str_object["pattern"] = f"^.*({re.escape(schema.props.substr)}).*$"

        return str_object

    def visit_list(self, schema: ListSchema, **kwargs: Any) -> dict[str, Any]:
        for prop in schema.props:
            if prop not in supported_props.ListProps:
                warnings.warn(f"Unsupported prop {prop} for type {schema.__str__()}", Warning)

        array_object: dict[str, Any] = {
            "type": "array"
        }

        if schema.props.len is not Nil:
            array_object["minItems"] = schema.props.len
            array_object["maxItems"] = schema.props.len

        if schema.props.min_len is not Nil:
            array_object["minItems"] = schema.props.min_len
        if schema.props.max_len is not Nil:
            array_object["maxItems"] = schema.props.max_len

        if schema.props.type is not Nil:
            array_object["items"] = schema.props.type.__accept__(self, **kwargs)
            return array_object

        if schema.props.elements is not Nil:
            array_object["prefixItems"] = []
            array_object["items"] = False
            for element in schema.props.elements:
                if is_ellipsis(element):
                    array_object["items"] = True
                    continue

                array_object["prefixItems"].append(element.__accept__(self, **kwargs))

        return array_object

    def visit_dict(self, schema: DictSchema, **kwargs: Any) -> dict[str, Any]:
        for prop in schema.props:
            if prop not in supported_props.DictProps:
                warnings.warn(f"Unsupported prop {prop} for type {schema.__str__()}", Warning)

        dict_object: dict[str, Any] = {
            "type": "object"
        }

        if schema.props.keys is Nil:
            return dict_object

        dict_object["additionalProperties"] = False
        dict_object["properties"] = {}
        required = []
        for key, (val, is_optional) in schema.props.keys.items():
            if is_ellipsis(key):
                dict_object["additionalProperties"] = True
                continue

            dict_object["properties"][key] = val.__accept__(self, **kwargs)
            if not is_optional:
                required.append(key)

        if required:
            dict_object["required"] = required

        return dict_object

    def visit_any(self, schema: AnySchema, **kwargs: Any) -> dict[str, Any]:
        for prop in schema.props:
            if prop not in supported_props.AnyProps:
                warnings.warn(f"Unsupported prop {prop} for type {schema.__str__()}", Warning)

        any_of = []

        if schema.props.types is not Nil:
            for obj in schema.props.types:
                any_of.append(obj.__accept__(self))

        return {"anyOf": any_of}

    def visit_bytes(self, schema: BytesSchema, **kwargs: Any) -> dict[str, Any]:
        warnings.warn("'schema.bytes' is not implemented")
        return {}

    def visit_datetime(self, schema: DateTimeSchema, **kwargs: Any) -> dict[str, Any]:
        for prop in schema.props:
            if prop not in supported_props.DateTimeProps:
                warnings.warn(f"Unsupported prop {prop} for type {schema.__str__()}", Warning)

        datetime_object: dict[str, Any] = {
            "type": "string",
            "format": "date-time",
        }

        if schema.props.value is not Nil:
            datetime_object["const"] = schema.props.value.isoformat()

        return datetime_object

    def visit_date(self, schema: DateSchema, **kwargs: Any) -> dict[str, Any]:
        for prop in schema.props:
            if prop not in supported_props.DateProps:
                warnings.warn(f"Unsupported prop {prop} for type {schema.__str__()}", Warning)

        date_object: dict[str, Any] = {
            "type": "string",
            "format": "date",
        }

        if schema.props.value is not Nil:
            date_object["const"] = schema.props.value.isoformat()

        return date_object

    def visit_uuid4(self, schema: UUID4Schema, **kwargs: Any) -> dict[str, Any]:
        for prop in schema.props:
            if prop not in supported_props.UUID4Props:
                warnings.warn(f"Unsupported prop {prop} for type {schema.__str__()}", Warning)

        uuid_object: dict[str, Any] = {
            "type": "string",
            "format": "uuid",
        }

        if schema.props.value is not Nil:
            uuid_object["const"] = str(schema.props.value)

        return uuid_object

    def visit_type_alias(self, schema: GenericTypeAliasSchema[TypeAliasPropsType],
                         **kwargs: Any) -> Any:
        return schema.props.type.__accept__(self, **kwargs)

    def visit_unordered(self, schema: ListSchema, **kwargs: Any) -> dict[str, Any]:
        for prop in schema.props:
            if prop not in supported_props.ListProps:
                warnings.warn(f"Unsupported prop {prop} for type {schema.__str__()}", Warning)

        array_object: dict[str, Any] = {
            "type": "array"
        }

        if schema.props.len is not Nil:
            array_object["minItems"] = schema.props.len
            array_object["maxItems"] = schema.props.len

        if schema.props.min_len is not Nil:
            array_object["minItems"] = schema.props.min_len
        if schema.props.max_len is not Nil:
            array_object["maxItems"] = schema.props.max_len

        if schema.props.type is not Nil:
            array_object["items"] = schema.props.type.__accept__(self, **kwargs)
            return array_object

        if schema.props.elements is not Nil:
            concrete_elements: list[dict[str, Any]] = []
            has_ellipsis = False
            for element in schema.props.elements:
                if is_ellipsis(element):
                    has_ellipsis = True
                    continue

                concrete_elements.append(element.__accept__(self, **kwargs))

            if len(concrete_elements) == 1 and has_ellipsis:
                array_object["contains"] = concrete_elements[0]
                array_object["items"] = True
            elif concrete_elements:
                if not has_ellipsis:
                    if "minItems" not in array_object:
                        array_object["minItems"] = len(concrete_elements)
                    if "maxItems" not in array_object:
                        array_object["maxItems"] = len(concrete_elements)

                if len(concrete_elements) == 1:
                    array_object["items"] = concrete_elements[0]
                else:
                    array_object["items"] = {"anyOf": concrete_elements}

                if has_ellipsis:
                    array_object["items"] = True
            elif has_ellipsis:
                array_object["items"] = True

        return array_object

    def visit_sdict(self, schema: DictSchema, **kwargs: Any) -> dict[str, Any]:
        return self.visit_dict(schema, **kwargs)

    def visit_uuid_str(self, schema: Any, **kwargs: Any) -> dict[str, Any]:
        for prop in schema.props:
            if prop not in supported_props.UUIDStrProps:
                warnings.warn(f"Unsupported prop {prop} for type {schema.__str__()}", Warning)

        uuid_object: dict[str, Any] = {
            "type": "string",
            "format": "uuid",
        }

        if schema.props.value is not Nil:
            uuid_object["const"] = schema.props.value

        if schema.props.is_lowercase is not Nil:
            uuid_object["pattern"] = _UUID_LOWERCASE_PATTERN
        elif schema.props.is_uppercase is not Nil:
            uuid_object["pattern"] = _UUID_UPPERCASE_PATTERN

        return uuid_object

    def visit_uuid(self, schema: Any, **kwargs: Any) -> dict[str, Any]:
        for prop in schema.props:
            if prop not in supported_props.UUID4Props:
                warnings.warn(f"Unsupported prop {prop} for type {schema.__str__()}", Warning)

        uuid_object: dict[str, Any] = {
            "type": "string",
            "format": "uuid",
        }

        if schema.props.value is not Nil:
            uuid_object["const"] = str(schema.props.value)

        return uuid_object

    def visit_numeric(self, schema: Any, **kwargs: Any) -> dict[str, Any]:
        for prop in schema.props:
            if prop not in supported_props.NumericProps:
                warnings.warn(f"Unsupported prop {prop} for type {schema.__str__()}", Warning)

        numeric_object: dict[str, Any] = {
            "type": "string",
            "pattern": "^[0-9]+$",
        }

        if schema.props.value is not Nil:
            numeric_object["const"] = schema.props.value

        if schema.props.min is not Nil:
            numeric_object["minLength"] = schema.props.min
        if schema.props.max is not Nil:
            numeric_object["maxLength"] = schema.props.max

        return numeric_object

    def visit_multi_dict(self, schema: Any, **kwargs: Any) -> dict[str, Any]:
        return self._visit_multi_dict(schema, **kwargs)

    def visit_ci_multi_dict(self, schema: Any, **kwargs: Any) -> dict[str, Any]:
        return self._visit_multi_dict(schema, **kwargs)

    def _visit_multi_dict(self, schema: Any, **kwargs: Any) -> dict[str, Any]:
        dict_object: dict[str, Any] = {
            "type": "object",
            "additionalProperties": False,
            "properties": {},
        }

        if schema.props.keys is Nil:
            return dict_object

        key_schemas: dict[str, list[dict[str, Any]]] = {}
        for key, val in schema.props.keys.items():
            key_schemas.setdefault(key, []).append(val.__accept__(self, **kwargs))

        required = []
        for key, schemas in key_schemas.items():
            if len(schemas) == 1:
                dict_object["properties"][key] = schemas[0]
            else:
                dict_object["properties"][key] = {"anyOf": schemas}
            required.append(key)

        dict_object["required"] = required
        return dict_object
