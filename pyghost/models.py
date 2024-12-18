# ---------------------------------------------------------------------------- #

import pydantic
from typing import Any, List, Optional

# ---------------------------------------------------------------------------- #


class MatcherConfig(pydantic.BaseModel):
    name: str
    label: str
    module: str
    cls: str
    languages: List[str]
    config: dict[Any, Any] = {}


class TransformerConfig(pydantic.BaseModel):
    name: str
    module: str
    cls: str
    config: dict[Any, Any] = {}


class OcrConfig(pydantic.BaseModel):
    name: str
    module: str
    cls: str
    languages: List[str]
    config: dict[Any, Any] = {}


class DocumentConfig(pydantic.BaseModel):
    highlighter_color: str
    text_color: str
    max_font_size: int
    font: str


class Config(pydantic.BaseModel):
    document: DocumentConfig
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


class OcrResult(pydantic.BaseModel):
    text: str
    words: List[Word]

# ---------------------------------------------------------------------------- #


class Match(pydantic.BaseModel):
    label: str
    matcher: str
    text: str
    start: int
    end: int

    touched: List[Word] = []

    model_label: Optional[str] = None

# ---------------------------------------------------------------------------- #


class Transformation(pydantic.BaseModel):
    word: Word
    replacement: str
    applied: bool = False


class TransformerResult(pydantic.BaseModel):
    source_text: str
    transformed_text: str
    transformations: List[Transformation]

# ---------------------------------------------------------------------------- #


class GhostResult(pydantic.BaseModel):
    matches: List[Match]
    transformation: TransformerResult

# ---------------------------------------------------------------------------- #
