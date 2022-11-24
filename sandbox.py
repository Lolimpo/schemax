import json

from district42 import optional, schema
from blahblah import fake

from schemax import to_json_schema

TestSchema = schema.dict({
    'str_with_len': schema.str.len(1, 10),
    'str_with_regex': schema.str.regex(r"[a-z0-9_]+"),
    'new_dict': schema.dict({
        'foo': schema.str.len(3)
    }),
    optional('str_with_alphabet'): schema.str.alphabet('abcdefg'),
    'int_with_min_max': schema.int.min(10).max(50),
    'int_with_value': schema.int(25),
    'float_with_value': schema.float(3.14),
    'bool': schema.bool(True),
    'null': schema.none,
    'any': schema.any(schema.str.len(12), schema.bool),
    'bytes': schema.bytes(b'123')
})

TestSchema2 = schema.list(schema.int.min(20)).len(1)

print(json.dumps(to_json_schema(TestSchema2, title="My Awesome Schema"), indent=2))
print(fake(TestSchema2))
