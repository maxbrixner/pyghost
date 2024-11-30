
# ---------------------------------------------------------------------------- #

import pydantic
import logging
from typing import Any, List, Optional

# ---------------------------------------------------------------------------- #

from ._base import BaseTransformer, TransformerResult
from ..matchers import Match

# ---------------------------------------------------------------------------- #


class LabelTransformer(BaseTransformer):
    """
    The label transformer replaces entities by their label.
    """
    class TransformerConfig(pydantic.BaseModel):
        """
        Use this pydantic model to define your transformer's config
        parameters.
        """
        prefix: str = "<"
        suffix: str = ">"

    def process(self, text: str, matches: List[Match]) -> TransformerResult:
        """
        Overwrite this method to implement your transformer's processing.
        """
        for match in matches:
            print(match)

        return TransformerResult(
            source_text=text,
            transformed_text=text,
            transformations={}
        )
