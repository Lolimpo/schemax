from baby_steps import given, then, when
from datetime import date, datetime
from uuid import UUID

from d42 import optional, schema

import district42_exp_types.numeric  # noqa: F401
import district42_exp_types.uuid_str  # noqa: F401
from district42_exp_types.unordered import UnorderedSchema
from schemax import to_json_schema


def test_none():
    with given:
        sch = schema.none
    with when:
        res = to_json_schema(sch, hide_draft=True)
    with then:
        assert res == {"type": "null"}


def test_bool():
    with given:
        sch = schema.bool
    with when:
        res = to_json_schema(sch, hide_draft=True)
    with then:
        assert res == {"type": "boolean"}


def test_bool_with_value():
    with given:
        sch = schema.bool(True)
    with when:
        res = to_json_schema(sch, hide_draft=True)
    with then:
        assert res == {"enum": [True]}


def test_int():
    with given:
        sch = schema.int
    with when:
        res = to_json_schema(sch, hide_draft=True)
    with then:
        assert res == {"type": "integer"}


def test_int_with_value():
    with given:
        sch = schema.int(3)
    with when:
        res = to_json_schema(sch, hide_draft=True)
    with then:
        assert res == {"type": "integer", "minimum": 3, "maximum": 3}


def test_int_with_min():
    with given:
        sch = schema.int.min(3)
    with when:
        res = to_json_schema(sch, hide_draft=True)
    with then:
        assert res == {"type": "integer", "minimum": 3}


def test_int_with_max():
    with given:
        sch = schema.int.max(3)
    with when:
        res = to_json_schema(sch, hide_draft=True)
    with then:
        assert res == {"type": "integer", "maximum": 3}


def test_int_with_min_max():
    with given:
        sch = schema.int.min(3).max(6)
    with when:
        res = to_json_schema(sch, hide_draft=True)
    with then:
        assert res == {"type": "integer", "minimum": 3, "maximum": 6}


def test_float():
    with given:
        sch = schema.float
    with when:
        res = to_json_schema(sch, hide_draft=True)
    with then:
        assert res == {"type": "number"}


def test_float_with_value():
    with given:
        sch = schema.float(3.14)
    with when:
        res = to_json_schema(sch, hide_draft=True)
    with then:
        assert res == {"type": "number", "minimum": 3.14, "maximum": 3.14}


def test_float_with_min():
    with given:
        sch = schema.float.min(3.14)
    with when:
        res = to_json_schema(sch, hide_draft=True)
    with then:
        assert res == {"type": "number", "minimum": 3.14}


def test_float_with_max():
    with given:
        sch = schema.float.max(3.14)
    with when:
        res = to_json_schema(sch, hide_draft=True)
    with then:
        assert res == {"type": "number", "maximum": 3.14}


def test_float_with_min_max():
    with given:
        sch = schema.float.min(3.14).max(6.28)
    with when:
        res = to_json_schema(sch, hide_draft=True)
    with then:
        assert res == {"type": "number", "minimum": 3.14, "maximum": 6.28}


def test_str():
    with given:
        sch = schema.str
    with when:
        res = to_json_schema(sch, hide_draft=True)
    with then:
        assert res == {"type": "string"}


def test_str_with_value():
    with given:
        sch = schema.str("test")
    with when:
        res = to_json_schema(sch, hide_draft=True)
    with then:
        assert res == {"type": "string", "const": "test"}


def test_str_with_len():
    with given:
        sch = schema.str.len(3)
    with when:
        res = to_json_schema(sch, hide_draft=True)
    with then:
        assert res == {"type": "string", "minLength": 3, "maxLength": 3}


def test_str_with_min():
    with given:
        sch = schema.str.len(3, ...)
    with when:
        res = to_json_schema(sch, hide_draft=True)
    with then:
        assert res == {"type": "string", "minLength": 3}


def test_str_with_max():
    with given:
        sch = schema.str.len(..., 3)
    with when:
        res = to_json_schema(sch, hide_draft=True)
    with then:
        assert res == {"type": "string", "maxLength": 3}


def test_str_with_min_max():
    with given:
        sch = schema.str.len(3, 14)
    with when:
        res = to_json_schema(sch, hide_draft=True)
    with then:
        assert res == {"type": "string", "minLength": 3, "maxLength": 14}


def test_str_with_regex():
    with given:
        sch = schema.str.regex(r"[A-Z-_]+")
    with when:
        res = to_json_schema(sch, hide_draft=True)
    with then:
        assert res == {"type": "string", "pattern": "[A-Z-_]+"}


def test_str_with_alphabet():
    with given:
        sch = schema.str.alphabet("abcd")
    with when:
        res = to_json_schema(sch, hide_draft=True)
    with then:
        assert res == {"type": "string", "pattern": "^(a|b|c|d)+$"}


def test_str_with_contains():
    with given:
        sch = schema.str.contains("TEST")
    with when:
        res = to_json_schema(sch, hide_draft=True)
    with then:
        assert res == {"type": "string", "pattern": "^.*(TEST).*$"}


def test_list():
    with given:
        sch = schema.list
    with when:
        res = to_json_schema(sch, hide_draft=True)
    with then:
        assert res == {"type": "array"}


def test_list_with_type_value():
    with given:
        sch = schema.list(schema.int)
    with when:
        res = to_json_schema(sch, hide_draft=True)
    with then:
        assert res == {"type": "array", "items": {"type": "integer"}}


def test_list_with_elements_value():
    with given:
        sch = schema.list([schema.int, schema.str])
    with when:
        res = to_json_schema(sch, hide_draft=True)
    with then:
        assert res == {
            "type": "array",
            "prefixItems": [{"type": "integer"}, {"type": "string"}],
            "items": False
        }


def test_list_with_elements_value_and_ellipsis():
    with given:
        sch = schema.list([schema.int, ...])
    with when:
        res = to_json_schema(sch, hide_draft=True)
    with then:
        assert res == {
            "type": "array",
            "prefixItems": [{"type": "integer"}],
            "items": True
        }


def test_list_with_min():
    with given:
        sch = schema.list.len(3, ...)
    with when:
        res = to_json_schema(sch, hide_draft=True)
    with then:
        assert res == {"type": "array", "minItems": 3}


def test_list_with_max():
    with given:
        sch = schema.list.len(..., 3)
    with when:
        res = to_json_schema(sch, hide_draft=True)
    with then:
        assert res == {"type": "array", "maxItems": 3}


def test_list_with_min_max():
    with given:
        sch = schema.list.len(3, 14)
    with when:
        res = to_json_schema(sch, hide_draft=True)
    with then:
        assert res == {"type": "array", "minItems": 3, "maxItems": 14}


def test_dict():
    with given:
        sch = schema.dict
    with when:
        res = to_json_schema(sch, hide_draft=True)
    with then:
        assert res == {"type": "object"}


def test_dict_with_value():
    with given:
        sch = schema.dict({"foo": schema.int})
    with when:
        res = to_json_schema(sch, hide_draft=True)
    with then:
        assert res == {
            "type": "object",
            "properties": {"foo": {"type": "integer"}},
            "required": ["foo"],
            "additionalProperties": False
        }


def test_dict_with_value_and_ellipsis():
    with given:
        sch = schema.dict({"foo": schema.int, ...: ...})
    with when:
        res = to_json_schema(sch, hide_draft=True)
    with then:
        assert res == {
            "type": "object",
            "properties": {"foo": {"type": "integer"}},
            "required": ["foo"],
            "additionalProperties": True
        }


def test_dict_with_optional_value():
    with given:
        sch = schema.dict({optional("foo"): schema.int})
    with when:
        res = to_json_schema(sch, hide_draft=True)
    with then:
        assert res == {
            "type": "object",
            "properties": {"foo": {"type": "integer"}},
            "additionalProperties": False
        }


def test_dict_with_optional_value_and_ellipsis():
    with given:
        sch = schema.dict({optional("foo"): schema.int, ...: ...})
    with when:
        res = to_json_schema(sch, hide_draft=True)
    with then:
        assert res == {
            "type": "object",
            "properties": {"foo": {"type": "integer"}},
            "additionalProperties": True
        }


def test_dict_with_value_and_properties():
    with given:
        sch = schema.dict({"foo": schema.int.min(3).max(14)})
    with when:
        res = to_json_schema(sch, hide_draft=True)
    with then:
        assert res == {
            "type": "object",
            "properties": {"foo": {"type": "integer", "minimum": 3, "maximum": 14}},
            "required": ["foo"],
            "additionalProperties": False
        }


def test_any():
    with given:
        sch = schema.any
    with when:
        res = to_json_schema(sch, hide_draft=True)
    with then:
        assert res == {"anyOf": []}


def test_any_with_values():
    with given:
        sch = schema.any(schema.int, schema.str)
    with when:
        res = to_json_schema(sch, hide_draft=True)
    with then:
        assert res == {"anyOf": [{"type": "integer"}, {"type": "string"}]}


def test_or_operator_with_values():
    with given:
        sch = schema.str("test") | schema.int.min(3)
    with when:
        res = to_json_schema(sch, hide_draft=True)
    with then:
        assert res == {
            "anyOf": [
                {"type": "string", "const": "test"},
                {"type": "integer", "minimum": 3}
            ]
        }


def test_float_with_precision():
    with given:
        sch = schema.float.precision(2)
    with when:
        res = to_json_schema(sch, hide_draft=True)
    with then:
        assert res == {"type": "number", "multipleOf": 0.01}


def test_datetime():
    with given:
        sch = schema.datetime
    with when:
        res = to_json_schema(sch, hide_draft=True)
    with then:
        assert res == {"type": "string", "format": "date-time"}


def test_datetime_with_value():
    with given:
        sch = schema.datetime(datetime(2020, 1, 1, 12, 30, 45))
    with when:
        res = to_json_schema(sch, hide_draft=True)
    with then:
        assert res == {
            "type": "string",
            "format": "date-time",
            "const": "2020-01-01T12:30:45",
        }


def test_date():
    with given:
        sch = schema.date
    with when:
        res = to_json_schema(sch, hide_draft=True)
    with then:
        assert res == {"type": "string", "format": "date"}


def test_date_with_value():
    with given:
        sch = schema.date(date(2020, 1, 1))
    with when:
        res = to_json_schema(sch, hide_draft=True)
    with then:
        assert res == {
            "type": "string",
            "format": "date",
            "const": "2020-01-01",
        }


def test_uuid4():
    with given:
        sch = schema.uuid4
    with when:
        res = to_json_schema(sch, hide_draft=True)
    with then:
        assert res == {"type": "string", "format": "uuid"}


def test_uuid4_with_value():
    with given:
        sch = schema.uuid4(UUID("12345678-1234-5678-1234-567812345678"))
    with when:
        res = to_json_schema(sch, hide_draft=True)
    with then:
        assert res == {
            "type": "string",
            "format": "uuid",
            "const": "12345678-1234-5678-1234-567812345678",
        }


def test_type_alias():
    with given:
        sch = schema.alias("MyInt", schema.int.min(1))
    with when:
        res = to_json_schema(sch, hide_draft=True)
    with then:
        assert res == {"type": "integer", "minimum": 1}


def test_unordered_list():
    with given:
        sch = UnorderedSchema()([schema.int, schema.str])
    with when:
        res = to_json_schema(sch, hide_draft=True)
    with then:
        assert res == {
            "type": "array",
            "minItems": 2,
            "maxItems": 2,
            "items": {"anyOf": [{"type": "integer"}, {"type": "string"}]},
        }


def test_unordered_contains():
    with given:
        sch = UnorderedSchema()([..., schema.int, ...])
    with when:
        res = to_json_schema(sch, hide_draft=True)
    with then:
        assert res == {
            "type": "array",
            "contains": {"type": "integer"},
            "items": True,
        }


def test_uuid_str_lowercase():
    with given:
        sch = schema.uuid_str.lowercase()
    with when:
        res = to_json_schema(sch, hide_draft=True)
    with then:
        assert res == {
            "type": "string",
            "format": "uuid",
            "pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
        }


def test_numeric_with_min_max():
    with given:
        sch = schema.numeric.min(2).max(5)
    with when:
        res = to_json_schema(sch, hide_draft=True)
    with then:
        assert res == {
            "type": "string",
            "pattern": "^[0-9]+$",
            "minLength": 2,
            "maxLength": 5,
        }
