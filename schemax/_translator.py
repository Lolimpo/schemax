import re
import warnings
from typing import Any, Dict

from d42.declaration import SchemaVisitor
from d42.declaration.types import (
    AnySchema,
    BoolSchema,
    BytesSchema,
    DictSchema,
    FloatSchema,
    GenericTypeAliasSchema,
    IntSchema,
    ListSchema,
    NoneSchema,
    StrSchema,
    TypeAliasPropsType,
)
from d42.utils import is_ellipsis
from niltype import Nil

from schemax import supported_props


class Translator(SchemaVisitor[Any]):
    def visit_none(self, schema: NoneSchema, **kwargs: Any) -> Dict[str, Any]:
        return {"type": "null"}

    def visit_bool(self, schema: BoolSchema, **kwargs: Any) -> Dict[str, Any]:
        for prop in schema.props:
            if prop not in supported_props.BoolProps:
                warnings.warn(f"Unsupported prop {prop} for type {schema.__str__()}", Warning)

        if schema.props.value is Nil:
            return {"type": "boolean"}

        return {"enum": [schema.props.value]}

    def visit_int(self, schema: IntSchema, **kwargs: Any) -> Dict[str, Any]:
        for prop in schema.props:
            if prop not in supported_props.IntProps:
                warnings.warn(f"Unsupported prop {prop} for type {schema.__str__()}", Warning)

        int_object: Dict[str, Any] = {
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

    def visit_float(self, schema: FloatSchema, **kwargs: Any) -> Dict[str, Any]:
        for prop in schema.props:
            if prop not in supported_props.FloatProps:
                warnings.warn(f"Unsupported prop {prop} for type {schema.__str__()}", Warning)

        number_object: Dict[str, Any] = {
            "type": "number"
        }

        if schema.props.value is not Nil:
            number_object["minimum"] = schema.props.value
            number_object["maximum"] = schema.props.value

        if schema.props.min is not Nil:
            number_object["minimum"] = schema.props.min
        if schema.props.max is not Nil:
            number_object["maximum"] = schema.props.max

        return number_object

    def visit_str(self, schema: StrSchema, **kwargs: Any) -> Dict[str, Any]:
        for prop in schema.props:
            if prop not in supported_props.StrProps:
                warnings.warn(f"Unsupported prop {prop} for type {schema.__str__()}", Warning)

        str_object: Dict[str, Any] = {
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

    def visit_list(self, schema: ListSchema, **kwargs: Any) -> Dict[str, Any]:
        for prop in schema.props:
            if prop not in supported_props.ListProps:
                warnings.warn(f"Unsupported prop {prop} for type {schema.__str__()}", Warning)

        array_object: Dict[str, Any] = {
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

    def visit_dict(self, schema: DictSchema, **kwargs: Any) -> Dict[str, Any]:
        for prop in schema.props:
            if prop not in supported_props.DictProps:
                warnings.warn(f"Unsupported prop {prop} for type {schema.__str__()}", Warning)

        dict_object: Dict[str, Any] = {
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

    def visit_any(self, schema: AnySchema, **kwargs: Any) -> Dict[str, Any]:
        for prop in schema.props:
            if prop not in supported_props.AnyProps:
                warnings.warn(f"Unsupported prop {prop} for type {schema.__str__()}", Warning)

        any_of = []

        if schema.props.types is not Nil:
            for obj in schema.props.types:
                any_of.append(obj.__accept__(self))

        return {"anyOf": any_of}

    def visit_bytes(self, schema: BytesSchema, **kwargs: Any) -> Dict[str, Any]:
        warnings.warn("'schema.bytes' is not implemented")
        return {}

    def visit_type_alias(self, schema: GenericTypeAliasSchema[TypeAliasPropsType],
                         **kwargs: Any) -> Any:
        warnings.warn("'schema.alias' is not implemented")
        return {}
