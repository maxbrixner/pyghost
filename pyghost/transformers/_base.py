
# ---------------------------------------------------------------------------- #

import pydantic
import logging
from typing import Any, List, Optional

# ---------------------------------------------------------------------------- #

from ..matchers import Match

# ---------------------------------------------------------------------------- #


class TransformerResult(pydantic.BaseModel):
    """
    This should not be overwritten or extended.
    """
    source_text: str
    transformed_text: str
    transformations: dict[Any, Any]  # todo

# ---------------------------------------------------------------------------- #


class BaseTransformer():
    """
    All transformers inherit from the BaseTransformer class. It provides basic
    config management and the interface to the pseudomizer.
    """
    class TransformerConfig(pydantic.BaseModel):
        """
        Use this pydantic model to define your transformer's config
        parameters.
        """
        pass

    config: TransformerConfig
    logger: logging.Logger

    def __init__(
        self,
        config: dict[Any, Any]
    ):
        """
        Initialize the transformer and assign the configuration.
        """
        self.config = self.TransformerConfig(**config)
        self.logger = logging.getLogger("pyghost.transformers")

    def process(self, text: str, matches: List[Match]) -> TransformerResult:
        """
        Overwrite this method to implement your transformer's processing.
        """
        return TransformerResult(
            source_text=text,
            transformed_text=text,
            transformations={}
        )

    def merge_overlapping_matches(self, matches: List[Match]) -> List[Match]:
        pass

# ---------------------------------------------------------------------------- #
