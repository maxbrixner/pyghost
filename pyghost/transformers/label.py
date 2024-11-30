
# ---------------------------------------------------------------------------- #

import pydantic
import logging
from typing import Any, List, Optional

# ---------------------------------------------------------------------------- #

from ._base import BaseTransformer, TransformerResult, Transformation
from ..matchers import Match

# ---------------------------------------------------------------------------- #


class LabelTransformer(BaseTransformer):
    """
    The label transformer replaces entities by their label, e.g. "Dublin" by
    "<location>".
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
        merged_matches = self.merge_overlapping_matches(matches)

        transformations = []
        for match in merged_matches:
            transformations.append(
                Transformation(
                    match=match,
                    replacement=f"{self.config.prefix}"
                    f"{match.label}"
                    f"{self.config.suffix}"
                )
            )

        return TransformerResult(
            source_text=text,
            transformed_text=text,
            transformations=transformations
        )
