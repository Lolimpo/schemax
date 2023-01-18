from baby_steps import given, then, when
from district42 import schema

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


def test_int():
    with given:
        sch = schema.int
    with when:
        res = to_json_schema(sch, hide_draft=True)
    with then:
        assert res == {"type": "integer"}


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
