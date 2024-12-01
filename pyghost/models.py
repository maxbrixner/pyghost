# ---------------------------------------------------------------------------- #

import pydantic
from typing import Any, List, Optional

# ---------------------------------------------------------------------------- #


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


class OcrConfig(pydantic.BaseModel):
    name: str
    module: str
    cls: str
    active: bool = True
    config: dict[Any, Any] = {}


class Config(pydantic.BaseModel):
    ocr: List[OcrConfig] = []
    matchers: List[MatcherConfig] = []
    transformers: List[TransformerConfig] = []

# ---------------------------------------------------------------------------- #


class Coordinates(pydantic.BaseModel):
    left: int
    top: int
    width: int
    height: int


class Word(pydantic.BaseModel):
    text: str
    start: int
    end: int
    page: int

    coordinates: Optional[Coordinates] = None

# ---------------------------------------------------------------------------- #


class Match(pydantic.BaseModel):
    """
    This should not be overwritten or extended.
    """
    label: str
    text: str
    start: int
    end: int

    context: Optional[str] = None
    source_labels: Optional[List[str]] = None
    ignore: bool = False
    merged: bool = False

# ---------------------------------------------------------------------------- #


class OcrResult(pydantic.BaseModel):
    text: str
    words: List[Word]

# ---------------------------------------------------------------------------- #


class Transformation(pydantic.BaseModel):
    match: Match
    replacement: str


class TransformerResult(pydantic.BaseModel):
    source_text: str
    transformed_text: str
    transformations: List[Transformation]

# ---------------------------------------------------------------------------- #
