from baby_steps import given, then, when
from d42 import optional, schema

from schemax import from_json_schema


def test_empty_schema():
    with given:
        jsch = {}
    with when:
        res = from_json_schema(jsch)
    with then:
        assert res == schema.any


def test_none():
    with given:
        jsch = {"type": "null"}
    with when:
        res = from_json_schema(jsch)
    with then:
        assert res == schema.none


def test_bool():
    with given:
        jsch = {"type": "boolean"}
    with when:
        res = from_json_schema(jsch)
    with then:
        assert res == schema.bool


def test_bool_with_value():
    with given:
        jsch = {"enum": [True]}
    with when:
        res = from_json_schema(jsch)
    with then:
        assert res == schema.bool(True)


def test_int():
    with given:
        jsch = {"type": "integer"}
    with when:
        res = from_json_schema(jsch)
    with then:
        assert res == schema.int


def test_int_with_value():
    with given:
        jsch = {"type": "integer", "minimum": 3, "maximum": 3}
    with when:
        res = from_json_schema(jsch)
    with then:
        assert res == schema.int(3)


def test_int_with_min():
    with given:
        jsch = {"type": "integer", "minimum": 3}
    with when:
        res = from_json_schema(jsch)
    with then:
        assert res == schema.int.min(3)


def test_int_with_exclusive_min():
    with given:
        jsch = {"type": "integer", "exclusiveMinimum": 3}
    with when:
        res = from_json_schema(jsch)
    with then:
        assert res == schema.int.min(4)


def test_int_with_max():
    with given:
        jsch = {"type": "integer", "maximum": 3}
    with when:
        res = from_json_schema(jsch)
    with then:
        assert res == schema.int.max(3)


def test_int_with_exclusive_max():
    with given:
        jsch = {"type": "integer", "exclusiveMaximum": 3}
    with when:
        res = from_json_schema(jsch)
    with then:
        assert res == schema.int.max(2)


def test_int_with_min_max():
    with given:
        jsch = {"type": "integer", "minimum": 3, "maximum": 4}
    with when:
        res = from_json_schema(jsch)
    with then:
        assert res == schema.int.min(3).max(4)


def test_int_with_exclusive_min_max():
    with given:
        jsch = {"type": "integer", "exclusiveMinimum": 1, "exclusiveMaximum": 4}
    with when:
        res = from_json_schema(jsch)
    with then:
        assert res == schema.int.min(2).max(3)


def test_number():
    with given:
        jsch = {"type": "number"}
    with when:
        res = from_json_schema(jsch)
    with then:
        assert res == schema.float | schema.int


def test_number_with_value():
    with given:
        jsch = {"type": "number", "minimum": 3.14, "maximum": 3.14}
    with when:
        res = from_json_schema(jsch)
    with then:
        assert res == schema.float(3.14) | schema.int(3)


def test_number_with_min():
    with given:
        jsch = {"type": "number", "minimum": 3.14}
    with when:
        res = from_json_schema(jsch)
    with then:
        assert res == schema.float.min(3.14) | schema.int.min(3)


def test_float_with_max():
    with given:
        jsch = {"type": "number", "maximum": 3.14}
    with when:
        res = from_json_schema(jsch)
    with then:
        assert res == schema.float.max(3.14) | schema.int.max(3)


def test_float_with_min_max():
    with given:
        jsch = {"type": "number", "minimum": 3.14, "maximum": 4.15}
    with when:
        res = from_json_schema(jsch)
    with then:
        assert res == schema.float.min(3.14).max(4.15) | schema.int.min(3).max(4)


def test_str():
    with given:
        jsch = {"type": "string"}
    with when:
        res = from_json_schema(jsch)
    with then:
        assert res == schema.str


def test_str_with_min():
    with given:
        jsch = {"type": "string", "minLength": 3}
    with when:
        res = from_json_schema(jsch)
    with then:
        assert res == schema.str.len(3, ...)


def test_str_with_max():
    with given:
        jsch = {"type": "string", "maxLength": 3}
    with when:
        res = from_json_schema(jsch)
    with then:
        assert res == schema.str.len(..., 3)


def test_str_with_min_max():
    with given:
        jsch = {"type": "string", "minLength": 3, "maxLength": 14}
    with when:
        res = from_json_schema(jsch)
    with then:
        assert res == schema.str.len(3, 14)


def test_str_with_same_min_max():
    with given:
        jsch = {"type": "string", "minLength": 3, "maxLength": 3}
    with when:
        res = from_json_schema(jsch)
    with then:
        assert res == schema.str.len(3)


def test_str_with_pattern_to_pattern():
    with given:
        jsch = {"type": "string", "pattern": "a+(b|c)+"}
    with when:
        res = from_json_schema(jsch)
    with then:
        assert res == schema.str.regex("a+(b|c)+")


def test_list():
    with given:
        jsch = {"type": "array"}
    with when:
        res = from_json_schema(jsch)
    with then:
        assert res == schema.list


def test_list_with_elements():
    with given:
        jsch = {
            "type": "array",
            "prefixItems": [{"type": "string"}, {"type": "integer"}],
            "items": False
        }
    with when:
        res = from_json_schema(jsch)
    with then:
        assert res == schema.list([schema.str, schema.int])


def test_list_with_elements_and_additions():
    with given:
        jsch = {
            "type": "array",
            "prefixItems": [{"type": "string"}, {"type": "integer"}],
            "items": True
        }
    with when:
        res = from_json_schema(jsch)
    with then:
        assert res == schema.list([schema.str, schema.int, ...])


def test_list_with_type_contains():
    with given:
        jsch = {"type": "array", "contains": {"type": "string"}}
    with when:
        res = from_json_schema(jsch)
    with then:
        assert res == schema.unordered([..., schema.str, ...])


def test_list_with_type_items():
    with given:
        jsch = {"type": "array", "items": {"type": "string"}}
    with when:
        res = from_json_schema(jsch)
    with then:
        assert res == schema.list(schema.str)


def test_list_with_min():
    with given:
        jsch = {"type": "array", "minItems": 3}
    with when:
        res = from_json_schema(jsch)
    with then:
        assert res == schema.list.len(3, ...)


def test_list_with_max():
    with given:
        jsch = {"type": "array", "maxItems": 3}
    with when:
        res = from_json_schema(jsch)
    with then:
        assert res == schema.list.len(..., 3)


def test_list_with_min_max():
    with given:
        jsch = {"type": "array", "minItems": 3, "maxItems": 14}
    with when:
        res = from_json_schema(jsch)
    with then:
        assert res == schema.list.len(3, 14)


def test_object():
    with given:
        jsch = {"type": "object"}
    with when:
        res = from_json_schema(jsch)
    with then:
        assert res == schema.dict


def test_object_with_required_key():
    with given:
        jsch = {
            "type": "object",
            "properties": {"list": {"type": "array"}},
            "required": ["list"],
            "additionalProperties": False
        }
    with when:
        res = from_json_schema(jsch)
    with then:
        assert res == schema.dict({"list": schema.list})


def test_object_with_required_key_and_additions():
    with given:
        jsch = {
            "type": "object",
            "properties": {"list": {"type": "array"}},
            "required": ["list"],
            "additionalProperties": True
        }
    with when:
        res = from_json_schema(jsch)
    with then:
        assert res == schema.dict({"list": schema.list, ...: ...})


def test_object_with_required_key_and_additions_2():
    with given:
        jsch = {
            "type": "object",
            "properties": {"list": {"type": "array"}},
            "required": ["list"]
        }
    with when:
        res = from_json_schema(jsch)
    with then:
        assert res == schema.dict({"list": schema.list, ...: ...})


def test_object_with_optional_key():
    with given:
        jsch = {
            "type": "object",
            "properties": {"list": {"type": "array"}, "int": {"type": "integer"}},
            "required": ["list"],
            "additionalProperties": False
        }
    with when:
        res = from_json_schema(jsch)
    with then:
        assert res == schema.dict({"list": schema.list, optional("int"): schema.int})


def test_object_without_additional_props():
    with given:
        jsch = {
            "type": "object",
            "properties": {"list": {"type": "array"}},
            "additionalProperties": False
        }
    with when:
        res = from_json_schema(jsch)
    with then:
        assert res == schema.dict({optional("list"): schema.list})


def test_object_with_additional_props():
    with given:
        jsch = {
            "type": "object",
            "properties": {"list": {"type": "array"}},
            "additionalProperties": True
        }
    with when:
        res = from_json_schema(jsch)
    with then:
        assert res == schema.dict({optional("list"): schema.list, ...: ...})


def test_object_with_additional_props_2():
    with given:
        jsch = {
            "type": "object",
            "properties": {"list": {"type": "array"}}
        }
    with when:
        res = from_json_schema(jsch)
    with then:
        assert res == schema.dict({optional("list"): schema.list, ...: ...})


def test_enum_none_value():
    with given:
        jsch = {
            "enum": [None]
        }
    with when:
        res = from_json_schema(jsch)
    with then:
        assert res == schema.none


def test_enum_bool_value():
    with given:
        jsch = {
            "enum": [True]
        }
    with when:
        res = from_json_schema(jsch)
    with then:
        assert res == schema.bool(True)


def test_enum_int_value():
    with given:
        jsch = {
            "enum": [123]
        }
    with when:
        res = from_json_schema(jsch)
    with then:
        assert res == schema.int(123)


def test_enum_float_value():
    with given:
        jsch = {
            "enum": [3.1415]
        }
    with when:
        res = from_json_schema(jsch)
    with then:
        assert res == schema.float(3.1415)


def test_enum_str_value():
    with given:
        jsch = {
            "enum": ["test"]
        }
    with when:
        res = from_json_schema(jsch)
    with then:
        assert res == schema.str("test")


def test_enum_list_value():
    with given:
        jsch = {
            "enum": [["test"]]
        }
    with when:
        res = from_json_schema(jsch)
    with then:
        assert res == schema.list


def test_enum_dict_value():
    with given:
        jsch = {
            "enum": [{"bob": "yes"}]
        }
    with when:
        res = from_json_schema(jsch)
    with then:
        assert res == schema.dict
