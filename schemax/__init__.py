from typing import Any, Optional

from district42 import GenericSchema
from district42.types import Schema

from ._translator import Translator
from ._version import version

__version__ = version
__all__ = ("Translator", "to_json_schema")

_translator = Translator()


def to_json_schema(schema: GenericSchema, title: Optional[str] = None, **kwargs: Any) -> Any:
    translation = schema.__accept__(_translator, **kwargs)
    if title is not None:
        translation['title'] = title
    return translation


Schema.__override__(Schema.__invert__.__name__, to_json_schema)
