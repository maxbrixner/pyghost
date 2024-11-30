# ---------------------------------------------------------------------------- #

import pydantic
from typing import Any, List

# ---------------------------------------------------------------------------- #


class TransformerConfig(pydantic.BaseModel):
    module: str


class MatcherConfig(pydantic.BaseModel):
    name: str
    module: str
    cls: str
    config: dict[Any, Any] = {}


class EntityConfig(pydantic.BaseModel):
    name: str
    active: bool = True
    matcher: MatcherConfig


class Config(pydantic.BaseModel):
    matchers: List[MatcherConfig] = []

# ---------------------------------------------------------------------------- #
