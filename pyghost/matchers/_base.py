# ---------------------------------------------------------------------------- #

import pydantic
import logging
from typing import Any, List, Optional

# ---------------------------------------------------------------------------- #


class Match(pydantic.BaseModel):
    """
    This should not be overwritten or extended.
    """
    label: Optional[str] = None  # set by pseudomizer

    text: str
    start: int
    end: int

    context: Optional[str] = None
    source_labels: Optional[List[str]] = None

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

    def __init__(
        self,
        config: dict[Any, Any]
    ):
        """
        Initialize the matcher and assign the configuration.
        """
        self.config = self.MatcherConfig(**config)
        self.logger = logging.getLogger("pyghost.matchers")

    def process(self, text: str) -> List[Match]:
        """
        Overwrite this method to implement your matcher's processing.
        """
        return []

# ---------------------------------------------------------------------------- #
