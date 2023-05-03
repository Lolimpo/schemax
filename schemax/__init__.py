from typing import Any, Optional

from district42 import GenericSchema
from district42.types import Schema

from ._from_json_schema import from_json_schema
from ._translator import Translator
from ._version import version

__version__ = version
__all__ = ("Translator", "to_json_schema", "from_json_schema")

_translator = Translator()


def to_json_schema(
    schema: GenericSchema,
    title: Optional[str] = None,
    hide_draft: Optional[bool] = False,
    **kwargs: Any
) -> Any:
    translation = schema.__accept__(_translator, **kwargs)

    if title is not None:
        translation = {'title': title, **translation}

    if not hide_draft:
        # Use latest version of json-schema draft
        translation = {'$schema': "https://json-schema.org/draft/2020-12/schema#", **translation}

    return translation


Schema.__override__(Schema.__invert__.__name__, to_json_schema)
