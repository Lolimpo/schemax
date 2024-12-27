# SchemaMaximal

[![PyPI](https://img.shields.io/pypi/v/schemax.svg?style=flat-square)](https://pypi.python.org/pypi/schemax/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/schemax?style=flat-square)](https://pypi.python.org/pypi/schemax/)
[![Python Version](https://img.shields.io/pypi/pyversions/schemax.svg?style=flat-square)](https://pypi.python.org/pypi/schemax/)

[district42](https://github.com/tsv1/district42) schemas ⇆ [JSON Schema](https://json-schema.org/)

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
$ schemax translate schema.json
```
```
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

## Supported d42 -> JSON Schema types and features

(✅ - done; 🔧 - planned support; ❌ - unsupportable)

* None:
    * ✅ [schema.none](https://github.com/tsv1/district42#schemanone)
* Bool:
    * ✅ [schema.bool](https://github.com/tsv1/district42#schemabool)
    * ✅ [schema.bool(value)](https://github.com/tsv1/district42#schemaboolvalue)
* Int:
    * ✅ [schema.int](https://github.com/tsv1/district42#schemaint)
    * ✅ [schema.int(value)](https://github.com/tsv1/district42#schemaintvalue)
    * ✅ [schema.int.min(value)](https://github.com/tsv1/district42#schemaintminvalue)
    * ✅ [schema.max(value)](https://github.com/tsv1/district42#schemaintmaxvalue)
* Float:
    * ✅ [schema.float](https://github.com/tsv1/district42#schemafloat)
    * ✅ [schema.float(value)](https://github.com/tsv1/district42#schemafloatvalue)
    * ✅ [schema.float.min(value)](https://github.com/tsv1/district42#schemafloatminvalue)
    * ✅ [schema.float.max(value)](https://github.com/tsv1/district42#schemafloatmaxvalue)
    * 🔧 [schema.float.precision(value)](https://github.com/tsv1/district42#schemafloatprecisionvalue)
* Str:
    * ✅ [schema.str](https://github.com/tsv1/district42#schemastr)
    * ✅ [schema.str(value)](https://github.com/tsv1/district42#schemastr)
    * ✅ [schema.str.len(length)](https://github.com/tsv1/district42#schemastrlenlength)
    * ✅ [schema.str.len(min_length, max_length)](https://github.com/tsv1/district42#schemastrlenmin_length-max_length)
    * ✅ [schema.str.alphabet(letters)](https://github.com/tsv1/district42#schemastralphabetletters)
    * ✅ [schema.str.contains(substr)](https://github.com/tsv1/district42#schemastrcontainssubstr)
    * ✅ [schema.regex(pattern)](https://github.com/tsv1/district42#schemastrregexpattern)
* List:
    * ✅ [schema.list](https://github.com/tsv1/district42#schemalist)
    * ✅ [schema.list(elements)](https://github.com/tsv1/district42#schemalistelements)
    * ✅ [schema.list(type)](https://github.com/tsv1/district42#schemalisttype)
    * ✅ [schema.list(type).len(length)](https://github.com/tsv1/district42#schemalisttypelenlength)
    * ✅ [schema.list(type).len(min_length, max_length)](https://github.com/tsv1/district42#schemalisttypelenmin_length-max_length)
* Dict:
    * ✅ [schema.dict](https://github.com/tsv1/district42#schemadict)
    * ✅ [schema.dict({key: value}) strict](https://github.com/tsv1/district42#schemadictkeys)
    * ✅ [schema.dict({key: value, ...: ...}) relaxed](https://github.com/tsv1/district42#schemadictkeys)
* Any:
    * ✅ [schema.any](https://github.com/tsv1/district42#schemaany)
    * ✅ [schema.any(*types)](https://github.com/tsv1/district42#schemaanytypes)
* ❌ [schema.bytes]()

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
