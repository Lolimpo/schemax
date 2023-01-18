"""
Sandbox file where you could try different stuff by yourself.
File will be deleted before merging!
"""

import json

from district42 import optional, schema

from schemax import to_json_schema
from schemax import from_json_schema


TestSchema = schema.dict({
    'str_with_len': schema.str.len(1, 10),
    'str_with_regex': schema.str.regex(r"[a-z0-9_]+"),
    'new_dict': schema.dict({
        optional('foo'): schema.str.len(3),
        'bar': schema.int.min(10)
    }),
    'new_list': schema.list(schema.int(15)),
    optional('str_with_alphabet'): schema.str.alphabet('abcdefg'),
    'int_with_min_max': schema.int.min(10).max(50),
    'int_with_value': schema.int(25),
    'float_with_value': schema.float(3.14),
    'bool': schema.bool(True),
    'null': schema.none
})

TestSchema2 = schema.list(schema.int(3)).len(1, 5)

print("To json-schema:\n", json.dumps(to_json_schema(TestSchema2, title="My Awesome Schema"), indent=2))
print("From json-schema:\n", from_json_schema(to_json_schema(TestSchema2)))

# with open("compose-spec.json", "r") as f:
#     data = json.load(f)
#     print(from_json_schema(data))
