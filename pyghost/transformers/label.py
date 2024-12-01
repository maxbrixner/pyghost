
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
        memory: bool = False

    memory: dict[str, str]
    counter: dict[str, int]

    def process(self, text: str, matches: List[Match]) -> TransformerResult:
        """
        Overwrite this method to implement your transformer's processing.
        """
        # merged_matches = self.merge_overlapping_matches(matches)

        transformations = self.create_transformations(matches=matches)

        transformed_text = self.apply_transformations(
            text=text,
            transformations=transformations
        )

        return TransformerResult(
            source_text=text,
            transformed_text=transformed_text,
            transformations=transformations
        )

    def __init__(self, config: dict[Any, Any]) -> None:
        super().__init__(config=config)
        self.counter = {}
        self.memory = {}

    def create_transformations(
        self,
        matches: List[Match]
    ) -> List[Transformation]:
        """
        Create transformations by replacing matches with their respective
        labels.
        """
        transformations = []
        for match in matches:
            if not self.config.memory:
                replacement = f"{self.config.prefix}{match.label}" \
                    f"{self.config.suffix}"
            else:
                if not match.label in self.counter:
                    self.counter[match.label] = 0

                if match.text in self.memory:
                    replacement = self.memory[match.text]
                else:
                    self.counter[match.label] += 1
                    replacement = f"{self.config.prefix}{match.label}" \
                        f"{self.counter[match.label]}{self.config.suffix}"
                    self.memory[match.text] = replacement

            transformations.append(
                Transformation(
                    match=match,
                    replacement=replacement,
                )
            )

        return transformations
