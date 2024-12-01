
# ---------------------------------------------------------------------------- #

import pydantic
import logging
from typing import Any, List, Optional

# ---------------------------------------------------------------------------- #

from ._base import BaseTransformer
from ..models import Match, TransformerResult, Transformation

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

    counter: dict[str, int]

    def __init__(self, config: dict[Any, Any]) -> None:
        """
        Initialize the label transformer.
        """
        super().__init__(config=config)
        self.counter = {}

    def create_transformations(
        self,
        matches: List[Match]
    ) -> List[Transformation]:
        """
        Create transformations by replacing matches with their respective
        labels. If memory is active, labels will be counted to give same
        entities the same labels.
        """
        transformations = []
        for match in matches:
            if not self.config.memory:
                replacement = match.label
            else:
                if not match.label in self.counter:
                    self.counter[match.label] = 0

                memory = self.from_memory(label=match.label, text=match.text)

                if memory:
                    self.logger.debug(
                        f"Getting replacment for '{match.text}' from memory.")
                    replacement = memory
                else:
                    self.counter[match.label] += 1
                    replacement = match.label
                    self.add_to_memory(
                        label=match.label,
                        text=match.text,
                        replacement=replacement
                    )

            transformations.append(
                Transformation(
                    match=match,
                    replacement=f"{self.config.prefix}"
                    f"{replacement}"
                    f"{self.counter[match.label]}"
                    f"{self.config.suffix}"
                )
            )

        return transformations

# ---------------------------------------------------------------------------- #
