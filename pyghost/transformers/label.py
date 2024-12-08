
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

    def create_transformations(
        self,
        matches: List[Match]
    ) -> List[Transformation]:
        """
        Create transformations by replacing words with their respective
        labels.
        """
        assert isinstance(self.config, self.TransformerConfig)
        
        transformations = []
        for match in matches:
            for index, word in enumerate(match.touched):
                (clean_text, suffix) = self.get_suffix(word.text)

                replacement = self.from_memory(
                    label=match.label, text=clean_text)

                if replacement is None:
                    replacement = match.label
                    self.add_to_memory(
                        label=match.label,
                        text=clean_text,
                        replacement=replacement
                    )

                transformations.append(
                    Transformation(
                        word=word,
                        replacement=f"{self.config.prefix}"
                        f"{replacement}"
                        f"{self.config.suffix}"
                        f"{suffix}"
                    )
                )

        return transformations

# ---------------------------------------------------------------------------- #
