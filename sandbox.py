"""
Sandbox file where you could try different stuff by yourself.
File will be deleted before merging!
"""

import json

from blahblah import fake
from district42 import schema

from schemax import to_json_schema
from schemax import from_json_schema

TestSchema = schema.list(schema.int)

print("Fake:\n", fake(TestSchema))
print("\nTo json-schema:\n",
      json.dumps(to_json_schema(TestSchema, title="My Awesome Schema"), indent=2))
print("\nFrom json-schema:\n", from_json_schema(to_json_schema(TestSchema)))
