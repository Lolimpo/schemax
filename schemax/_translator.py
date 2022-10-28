import warnings
from typing import Any, Dict

from district42 import SchemaVisitor, SchemaVisitorReturnType
from district42.types import (AnySchema, BoolSchema, BytesSchema, ConstSchema, DictSchema,
                              FloatSchema, GenericTypeAliasSchema, IntSchema, ListSchema,
                              NoneSchema, StrSchema, TypeAliasPropsType)
from district42.utils import is_ellipsis
from niltype import Nil


class Translator(SchemaVisitor[Any]):
    def visit_none(self, schema: NoneSchema, **kwargs: Any) -> SchemaVisitorReturnType:
        pass

    def visit_bool(self, schema: BoolSchema, **kwargs: Any) -> SchemaVisitorReturnType:
        pass

    def visit_int(self, schema: IntSchema, **kwargs: Any) -> SchemaVisitorReturnType:
        pass

    def visit_float(self, schema: FloatSchema, **kwargs: Any) -> SchemaVisitorReturnType:
        pass

    def visit_str(self, schema: StrSchema, **kwargs: Any) -> Dict[Any, Any]:
        str_object: Dict[str, Any] = {
            "type": "string"
        }

        if schema.props.pattern is not Nil:
            warnings.warn("Be aware that escape-sequences are unsupported in json-schemas regexes,"
                          " currently we can't do reformation and provide them 'as it is'."
                          "\nUse at our own risk", Warning)
            str_object["pattern"] = schema.props.pattern

        if schema.props.min_len is not Nil:
            str_object["minLength"] = schema.props.min_len
        if schema.props.max_len is not Nil:
            str_object["maxLength"] = schema.props.max_len
        return str_object

    def visit_list(self, schema: ListSchema, **kwargs: Any) -> SchemaVisitorReturnType:
        pass

    def visit_dict(self, schema: "DictSchema", **kwargs: Any) -> Dict[Any, Any]:
        translated: Dict[Any, Any] = {
            "type": "object"
        }

        if schema.props.keys is Nil:
            return translated

        translated['properties'] = {}
        required = []
        for key, (val, is_optional) in schema.props.keys.items():
            if is_ellipsis(key):
                continue

            translated['properties'][key] = val.__accept__(self, **kwargs)
            if not is_optional:
                required.append(key)

        translated['required'] = required

        return translated

    def visit_any(self, schema: AnySchema, **kwargs: Any) -> SchemaVisitorReturnType:
        pass

    def visit_const(self, schema: ConstSchema, **kwargs: Any) -> SchemaVisitorReturnType:
        pass

    def visit_bytes(self, schema: BytesSchema, **kwargs: Any) -> SchemaVisitorReturnType:
        pass

    def visit_type_alias(self, schema: GenericTypeAliasSchema[TypeAliasPropsType],
                         **kwargs: Any) -> Any:
        pass
