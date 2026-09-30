from typing import Any

from d42.declaration import GenericSchema
from d42.declaration.types import Schema

from ._config import Config
from ._data_collector import SchemaData, collect_schema_data
from ._from_json_schema import _from_json_schema
from ._openapi_normalizer import openapi_normalizer
from ._translator import Translator
from ._memoizer import Memoizer

__all__ = (
    "Config",
    "SchemaData",
    "Translator",
    "collect_schema_data",
    "from_json_schema",
    "to_json_schema",
    "Memoizer"
)

_translator = Translator()


def to_json_schema(
    schema: GenericSchema,
    title: str | None = None,
    hide_draft: bool | None = False,
    **kwargs: Any
) -> Any:
    translation = schema.__accept__(_translator, **kwargs)

    if title is not None:
        translation = {'title': title, **translation}

    if not hide_draft:
        # Use latest version of json-schema draft
        translation = {'$schema': "https://json-schema.org/draft/2020-12/schema#", **translation}

    return translation


def from_json_schema(value: dict[Any, Any]) -> GenericSchema:
    normalized_value = openapi_normalizer(value)
    return _from_json_schema(normalized_value)


Schema.__override__(Schema.__invert__.__name__, to_json_schema)
