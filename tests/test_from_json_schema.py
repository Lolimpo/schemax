from baby_steps import given, then, when
from district42 import schema

from schemax import from_json_schema


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


def test_int_with_max():
    with given:
        jsch = {"type": "integer", "maximum": 3}
    with when:
        res = from_json_schema(jsch)
    with then:
        assert res == schema.int.max(3)


def test_int_with_min_max():
    with given:
        jsch = {"type": "integer", "minimum": 3, "maximum": 4}
    with when:
        res = from_json_schema(jsch)
    with then:
        assert res == schema.int.min(3).max(4)


def test_float():
    with given:
        jsch = {"type": "number"}
    with when:
        res = from_json_schema(jsch)
    with then:
        assert res == schema.float


def test_float_with_value():
    with given:
        jsch = {"type": "number", "minimum": 3.14, "maximum": 3.14}
    with when:
        res = from_json_schema(jsch)
    with then:
        assert res == schema.float(3.14)


def test_float_with_min():
    with given:
        jsch = {"type": "number", "minimum": 3.14}
    with when:
        res = from_json_schema(jsch)
    with then:
        assert res == schema.float.min(3.14)


def test_float_with_max():
    with given:
        jsch = {"type": "number", "maximum": 3.14}
    with when:
        res = from_json_schema(jsch)
    with then:
        assert res == schema.float.max(3.14)


def test_float_with_min_max():
    with given:
        jsch = {"type": "number", "minimum": 3.14, "maximum": 4.15}
    with when:
        res = from_json_schema(jsch)
    with then:
        assert res == schema.float.min(3.14).max(4.15)


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
        assert res == schema.str.len(3)


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


def test_str_with_pattern():
    with given:
        jsch = {"type": "string", "pattern": "(a+b)+"}
    with when:
        res = from_json_schema(jsch)
    with then:
        assert res == schema.str.regex(r"(a+b)+")


def test_list():
    with given:
        jsch = {"type": "array"}
    with when:
        res = from_json_schema(jsch)
    with then:
        assert res == schema.list


def test_list_with_min():
    with given:
        jsch = {"type": "array", "minItems": 3}
    with when:
        res = from_json_schema(jsch)
    with then:
        assert res == schema.list.len(3)


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

