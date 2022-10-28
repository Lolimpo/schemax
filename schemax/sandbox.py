import json

from district42 import optional, schema

from schemax import to_json_schema

TestSchema = schema.dict({
    'str_with_len': schema.str.len(1, 10),
    'str_with_regex': schema.str.regex(r"[a-z0-9_]+"),
    optional('str_with_alphabet'): schema.str.alphabet('abcdefg')
})

print(json.dumps(to_json_schema(TestSchema, title="My Awesome Schema"), indent=2))
