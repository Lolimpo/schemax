# SchemaMaximal

[district42](https://github.com/tsv1/district42) schemas ⇆ [JSON Schema](https://json-schema.org/)

## Installation

```sh
pip3 install schemax
```

## Usage

```pycon
>>> import schemax
>>> from district42 import schema
>>> ExampleSchema = schema.str.len(1, 10)
>>> schemax.to_json_schema(ExampleSchema)
{'type': 'string', 'minLength': 1, 'maxLength': 10}
```

## Supported d42 -> JSON Schema types and features

(✅ - done; 🔧 - planned support; ❌ - unsupportable)

* None:
    * ✅ schema.none
* Bool:
    * ✅ schema.bool
    * 🔧 schema.bool(value)
* Int:
    * ✅ schema.int
    * ✅ schema.int(value)
    * ✅ schema.int.min(value)
    * ✅ schema.max(value)
* Float:
    * ✅ schema.float
    * ✅ schema.float(value)
    * ✅ schema.float.min(value)
    * ✅ schema.float.max(value)
    * schema.float.precision(value)
* Str:
    * ✅ schema.str
    * ❌ schema.str(value)
    * ✅ schema.str.len(length)
    * ✅ schema.str.len(min_length, max_length)
    * ✅ schema.str.alphabet(letters)
    * 🔧 schema.str.contains(substr)
    * ✅ schema.regex(pattern)
* List:
    * ✅ schema.list
    * ✅ schema.list(elements)
    * ✅ schema.list(type)
    * ✅ schema.list.len(length)
    * ✅ schema.list.len(min_length, max_length)
* Dict:
    * ✅ schema.dict
    * ✅ schema.dict(keys)
* Any:
    * ✅ schema.any
    * ✅ schema.any(*types)
* ❌ schema.const
* ❌ schema.bytes

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
* ✅ [number](http://json-schema.org/understanding-json-schema/reference/numeric.html#number)
    * ✅ [minimum](http://json-schema.org/understanding-json-schema/reference/numeric.html#range)
    * ✅ [maximum](http://json-schema.org/understanding-json-schema/reference/numeric.html#range)
    * ❌ [exclusiveMinimum](http://json-schema.org/understanding-json-schema/reference/numeric.html#range)
    * ❌ [exclusiveMaximum](http://json-schema.org/understanding-json-schema/reference/numeric.html#range)
* ✅ [string](http://json-schema.org/understanding-json-schema/reference/string.html)
    * ✅ [minLength](http://json-schema.org/understanding-json-schema/reference/string.html#length)
    * ✅ [maxLength](http://json-schema.org/understanding-json-schema/reference/string.html#length)
    * ✅ [pattern](http://json-schema.org/understanding-json-schema/reference/string.html#regular-expressions)
    * ✅ [format](http://json-schema.org/understanding-json-schema/reference/string.html#format)
* ✅ [array](http://json-schema.org/understanding-json-schema/reference/array.html)
    * ✅ [items](http://json-schema.org/understanding-json-schema/reference/array.html#items)
    * ✅ [length](http://json-schema.org/understanding-json-schema/reference/array.html#length)
    * ✅ [prefixItems](http://json-schema.org/understanding-json-schema/reference/array.html#tuple-validation)
    * ✅ [unevaluatedItems](http://json-schema.org/understanding-json-schema/reference/array.html#unevaluated-items)
* ✅ [object](http://json-schema.org/understanding-json-schema/reference/object.html)
    * ✅ [properties](http://json-schema.org/understanding-json-schema/reference/object.html#properties)
    * ❌ [patterProperties](http://json-schema.org/understanding-json-schema/reference/object.html#pattern-properties)
    * ❌ [additionalProperties](http://json-schema.org/understanding-json-schema/reference/object.html#additional-properties)
    * ✅ [requiredProperties](http://json-schema.org/understanding-json-schema/reference/object.html#additional-properties)
    * ❌ [propertyName](http://json-schema.org/understanding-json-schema/reference/object.html#property-names)
    * ❌ [size](http://json-schema.org/understanding-json-schema/reference/object.html#size)
