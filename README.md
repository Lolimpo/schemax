# SchemaMaximal

[district42](https://github.com/nikitanovosibirsk/district42) schemas ⇆ [JSON Schema](https://json-schema.org/)

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
