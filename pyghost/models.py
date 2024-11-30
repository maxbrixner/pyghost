# ---------------------------------------------------------------------------- #

import pydantic
from typing import Any, List

# ---------------------------------------------------------------------------- #


class TransformerConfig(pydantic.BaseModel):
    module: str


class MatcherConfig(pydantic.BaseModel):
    name: str
    label: str
    module: str
    cls: str
    active: bool = True
    config: dict[Any, Any] = {}


class TransformerConfig(pydantic.BaseModel):
    name: str
    module: str
    cls: str
    active: bool = True
    config: dict[Any, Any] = {}


class Config(pydantic.BaseModel):
    matchers: List[MatcherConfig] = []
    transformers: List[TransformerConfig] = []

# ---------------------------------------------------------------------------- #
