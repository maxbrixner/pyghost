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
    context: Optional[str] = None
    start: int
    end: int

# ---------------------------------------------------------------------------- #


class BaseMatcher():

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
        Initialize the matcher and assign the matcher's configuration.
        """
        self.config = self.MatcherConfig(**config)
        self.logger = logging.getLogger("pyghost.matchers")

    def process(self, text: str) -> List[Match]:
        """
        Overwrite this method to implement your matcher's processing.
        """
        return []

# ---------------------------------------------------------------------------- #
