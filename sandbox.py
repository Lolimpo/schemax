"""
Sandbox file where you could try different stuff by yourself.
File will be deleted before merging!
"""

import json

from blahblah import fake
from district42 import schema

from schemax import to_json_schema
from schemax import from_json_schema

TestSchema = schema.str("en") | schema.int(3)

print("fake:\n", fake(TestSchema))
print("To json-schema:\n",
      json.dumps(to_json_schema(TestSchema, title="My Awesome Schema"), indent=2))
print("From json-schema:\n", from_json_schema(to_json_schema(TestSchema)))
