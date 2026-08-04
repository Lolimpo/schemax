# SchemaMaximal

[![PyPI](https://img.shields.io/pypi/v/schemax.svg?style=flat-square)](https://pypi.python.org/pypi/schemax/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/schemax?style=flat-square)](https://pypi.python.org/pypi/schemax/)
[![Python Version](https://img.shields.io/pypi/pyversions/schemax.svg?style=flat-square)](https://pypi.python.org/pypi/schemax/)

[d42](https://d42.sh/) schemas ⇆ [JSON Schema](https://json-schema.org/)

## Installation

```sh
pip3 install schemax
```

## Usage

### Translation

```pycon
>>> import schemax
>>> from d42 import schema
>>> ExampleSchema = schema.str.len(1, 10)
>>> schemax.to_json_schema(ExampleSchema)
{'type': 'string', 'minLength': 1, 'maxLength': 10}
```

Also, you could use schemax to translate from JSON-Schema to d42 and ~~generate tests interfaces~~ (in future releases) via command line:

```shell
schemax translate schema.json
```

```shell
Translation from JSON-Schema to d42-schema for schema.json:
schema.dict({
    'number': schema.int.min(1),
    optional('street_name'): schema.str,
    ...: ...
})
```

`schema.json:`

```json
{
  "type": "object",
  "properties": {
    "number": { "type": "integer", "minimum": 1 },
    "street_name": { "type": "string" }
  },
  "required": ["number"],
  "additionalProperties": true
}
```

### Generation

```shell
schemax generate my-schema.yml
```

This command will generate request and response schemas files, API interface and basic scenarios.

You could add basic url to your API as following: `--base-url="http://api.example.com"`.

Making your schemas and interfaces more "friendly" could `--humanize` flag.

### Using `SchemaData` object in code

```python
import yaml
from schemax import collect_schema_data, SchemaData 

from typing import List

# Also could be JSON OpenAPI file
with open('my_openapi.yaml') as schema_file:
    raw_schema = yaml.load(schema_file, yaml.FullLoader)
    
    parsed_data: List[SchemaData] = collect_schema_data(raw_schema)
    for item in parsed_data:
        print(item.path)
        print(item.response_schema_d42)
        ...
```

All the data is stored in SchemaData object, which has the following fields:

* http_method: HTTP method of the request.
* path: URL path of the request.
* converted_path: URL path converted to the camel-case for usage in schemax generation.
* args: Arguments of the request.
* queries: Query parameters of the request. Currently unsupported and always '[]'.
* interface_method: Interface name for usage in schemax generation.
* interface_method_humanized: Interface 'humanized' name for usage in schemax generation.
* status: Status code for specified schemas.
* schema_prefix: Schema prefix name for usage in schemax generation.
* schema_prefix_humanized: Schema prefix 'humanized' name for user in schemax generation.
* response_schema: Normalized response schema (without $ref).
* response_schema_d42: Converted to d42 response_schema.
* request_schema: Normalized request schema (without $ref).
* request_schema_d42: Converted to d42 request_schema.
* tags: Tags of the request from OpenAPI schema.

## Supported d42 -> JSON Schema types and features

(✅ - done; 🔧 - planned support; ❌ - unsupportable)

* None:
  * ✅ [schema.none](https://d42.sh/docs/types/scalar-types#none)
* Bool:
  * ✅ [schema.bool](https://d42.sh/docs/types/scalar-types#bool)
  * ✅ [schema.bool(value)](https://d42.sh/docs/types/scalar-types#schemaboolvalue)
* Int:
  * ✅ [schema.int](https://d42.sh/docs/types/scalar-types#schemaint)
  * ✅ [schema.int(value)](https://d42.sh/docs/types/scalar-types#schemaintvalue)
  * ✅ [schema.int.min(value)](https://d42.sh/docs/types/scalar-types#schemaintminvalue)
  * ✅ [schema.int.max(value)](https://d42.sh/docs/types/scalar-types#schemaintmaxvalue)
* Float:
  * ✅ [schema.float](https://d42.sh/docs/types/scalar-types#schemafloat)
  * ✅ [schema.float(value)](https://d42.sh/docs/types/scalar-types#schemafloatvalue)
  * ✅ [schema.float.min(value)](https://d42.sh/docs/types/scalar-types#schemafloatminvalue)
  * ✅ [schema.float.max(value)](https://d42.sh/docs/types/scalar-types#schemafloatmaxvalue)
  * ✅ [schema.float.precision(value)](https://d42.sh/docs/types/scalar-types#schemafloatprecisionvalue)
* Str:
  * ✅ [schema.str](https://d42.sh/docs/types/scalar-types#schemastr)
  * ✅ [schema.str(value)](https://d42.sh/docs/types/scalar-types#schemastr)
  * ✅ [schema.str.len(length)](https://d42.sh/docs/types/scalar-types#schemastrlenlength)
  * ✅ [schema.str.len(min_length, max_length)](https://d42.sh/docs/types/scalar-types#schemastrlenmin_length-max_length)
  * ✅ [schema.str.alphabet(letters)](https://d42.sh/docs/types/scalar-types#schemastralphabetletters)
  * ✅ [schema.str.contains(substr)](https://d42.sh/docs/types/scalar-types#schemastrcontainssubstr)
  * ✅ [schema.str.regex(pattern)](https://d42.sh/docs/types/scalar-types#schemastrregexpattern)
* List:
  * ✅ [schema.list](https://d42.sh/docs/types/container-types/list#schemalist)
  * ✅ [schema.list(elements)](https://d42.sh/docs/types/container-types/list#schemalistelements)
  * ✅ [schema.list(type)](https://d42.sh/docs/types/container-types/list#schemalisttype)
  * ✅ [schema.list(type).len(length)](https://d42.sh/docs/types/container-types/list)
  * ✅ [schema.list(type).len(min_length, max_length)](https://d42.sh/docs/types/container-types/list)
* Dict:
  * ✅ [schema.dict](https://d42.sh/docs/types/container-types/dict#schemadict)
  * ✅ [schema.dict({key: value}) strict](https://d42.sh/docs/types/container-types/dict#schemadictkeys)
  * ✅ [schema.dict({key: value, ...: ...}) relaxed](https://d42.sh/docs/types/container-types/dict#schemadictkeys)
* Any:
  * ✅ [schema.any](https://d42.sh/docs/types/container-types/any#schemaany)
  * ✅ [schema.any(*types)](https://d42.sh/docs/types/container-types/any#schemaanytypes)
* Date:
  * ✅ [schema.date](https://d42.sh/docs/types/scalar-types#date)
  * ✅ [schema.date(value)](https://d42.sh/docs/types/scalar-types#schemadatevalue)
* Datetime:
  * ✅ [schema.datetime](https://d42.sh/docs/types/scalar-types#datetime)
  * ✅ [schema.datetime(value)](https://d42.sh/docs/types/scalar-types#schemadatetimevalue)
* UUID:
  * ✅ [schema.uuid4](https://d42.sh/docs/types/scalar-types#uuid4)
  * ✅ [schema.uuid4(value)](https://d42.sh/docs/types/scalar-types#schemauuid4value)
* Type Alias:
  * ✅ [schema.alias(name, schema)](https://d42.sh/docs/types/type-aliases) (unwraps to inner schema)
* ❌ [schema.bytes](https://d42.sh/docs/types/scalar-types#bytes)

## Supported JSON Schema -> d42 types and features

(✅ - done; 🔧 - planned support; ❌ - unsupportable)

* ✅ [null](http://json-schema.org/understanding-json-schema/reference/null.html)
* ✅ [boolean](http://json-schema.org/understanding-json-schema/reference/boolean.html)
* ✅ [integer](http://json-schema.org/understanding-json-schema/reference/numeric.html#integer)
  * ✅ [minimum](http://json-schema.org/understanding-json-schema/reference/numeric.html#range)
  * ✅ [maximum](http://json-schema.org/understanding-json-schema/reference/numeric.html#range)
  * ✅ [exclusiveMinimum](http://json-schema.org/understanding-json-schema/reference/numeric.html#range)
  Keep in mind, that we're just taking exclusiveMinimum + 1 as schema.int.min 
  * ✅ [exclusiveMaximum](http://json-schema.org/understanding-json-schema/reference/numeric.html#range)
  Keep in mind, that we're just taking exclusiveMaximum - 1 as schema.int.max
  * ❌ [multiples](http://json-schema.org/understanding-json-schema/reference/numeric.html?highlight=multipleof#multiples)
* ✅ [number](http://json-schema.org/understanding-json-schema/reference/numeric.html#number)
  * ✅ [minimum](http://json-schema.org/understanding-json-schema/reference/numeric.html#range)
  * ✅ [maximum](http://json-schema.org/understanding-json-schema/reference/numeric.html#range)
  * 🔧 [exclusiveMinimum](http://json-schema.org/understanding-json-schema/reference/numeric.html#range)
  * 🔧 [exclusiveMaximum](http://json-schema.org/understanding-json-schema/reference/numeric.html#range)
  * ❌ [multiples](http://json-schema.org/understanding-json-schema/reference/numeric.html?highlight=multipleof#multiples)
* ✅ [string](http://json-schema.org/understanding-json-schema/reference/string.html)
  * ✅ [minLength](http://json-schema.org/understanding-json-schema/reference/string.html#length)
  * ✅ [maxLength](http://json-schema.org/understanding-json-schema/reference/string.html#length)
  * ✅ [pattern](http://json-schema.org/understanding-json-schema/reference/string.html#regular-expressions)
  * ❌ [format](http://json-schema.org/understanding-json-schema/reference/string.html#format)
* ✅ [array](http://json-schema.org/understanding-json-schema/reference/array.html)
  * ✅ [items](http://json-schema.org/understanding-json-schema/reference/array.html#items)
  * ✅ [length](http://json-schema.org/understanding-json-schema/reference/array.html#length)
  * ✅ [prefixItems](http://json-schema.org/understanding-json-schema/reference/array.html#tuple-validation)
  * ✅ [unevaluatedItems](http://json-schema.org/understanding-json-schema/reference/array.html#unevaluated-items)
  * ❌ [uniqueness](http://json-schema.org/understanding-json-schema/reference/array.html#uniqueness)
* ✅ [object](http://json-schema.org/understanding-json-schema/reference/object.html)
  * ✅ [properties](http://json-schema.org/understanding-json-schema/reference/object.html#properties)
  * ❌ [patterProperties](http://json-schema.org/understanding-json-schema/reference/object.html#pattern-properties)
  * ❌ [additionalProperties](http://json-schema.org/understanding-json-schema/reference/object.html#additional-properties)
  * ✅ [requiredProperties](http://json-schema.org/understanding-json-schema/reference/object.html#additional-properties)
  * ❌ [propertyName](http://json-schema.org/understanding-json-schema/reference/object.html#property-names)
  * ❌ [size](http://json-schema.org/understanding-json-schema/reference/object.html#size)
