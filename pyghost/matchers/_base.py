# ---------------------------------------------------------------------------- #

import pydantic
import logging
from typing import Any, List, Optional

# ---------------------------------------------------------------------------- #

from ..models import Match

# ---------------------------------------------------------------------------- #


class BaseMatcher():
    """
    All matchers inherit from the BaseMatcher class. It provides basic config
    management and the interface to the pseudomizer.
    """
    class MatcherConfig(pydantic.BaseModel):
        """
        Use this pydantic model to define your matcher's config
        parameters.
        """
        pass

    config: MatcherConfig
    logger: logging.Logger
    label: str

    def __init__(
        self,
        label: str,
        config: dict[Any, Any]
    ):
        """
        Initialize the matcher and assign the configuration.
        """
        self.config = self.MatcherConfig(**config)
        self.logger = logging.getLogger("pyghost.matchers")
        self.label = label

    def process(self, text: str) -> List[Match]:
        """
        Overwrite this method to implement your matcher's processing.
        """
        return []

# ---------------------------------------------------------------------------- #
