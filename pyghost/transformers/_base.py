
# ---------------------------------------------------------------------------- #

import pydantic
import logging
from typing import Any, List, Optional

# ---------------------------------------------------------------------------- #

from ..matchers import Match

# ---------------------------------------------------------------------------- #


class Transformation(pydantic.BaseModel):
    match: Match
    replacement: str


class TransformerResult(pydantic.BaseModel):
    """
    This should not be overwritten or extended.
    """
    source_text: str
    transformed_text: str
    transformations: List[Transformation]

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
        self.merge_overlapping_matches(matches=matches)

        return TransformerResult(
            source_text=text,
            transformed_text=text,
            transformations={}
        )

    def merge_overlapping_matches(self, matches: List[Match]) -> List[Match]:
        if len(matches) < 1:
            return []

        merged = []
        for new_match in matches:
            append = True
            for index, old_match in enumerate(merged):
                # new match is a subset of the old match:
                # old match dominates
                if new_match.start >= old_match.start \
                        and new_match.end <= old_match.end:
                    self.logger.debug(
                        f"Match '{new_match.text}' is subset of match "
                        f"'{old_match.text}'. Will skip.")
                    append = False
                    continue

                # new match is a superset of the old match:
                # new match dominates
                if new_match.start <= old_match.start \
                        and new_match.end >= old_match.end:
                    self.logger.debug(
                        f"Match '{new_match.text}' is real superset of match "
                        f"'{old_match.text}'. Will replace.")
                    merged[index] = new_match.copy()
                    append = False
                    continue

                # new match overlaps old match
                # ???
                if (new_match.start < old_match.start
                        and new_match.end < old_match.end
                        and new_match.end > old_match.start) or \
                   (new_match.start > old_match.start
                        and new_match.start < old_match.end
                        and new_match.end > old_match.end):
                    # old_match.start = min(new_match.start, old_match.start)
                    # old_match.end = max(old_match.end, old_match.end)
                    raise Exception("WHAT TO DO?")  # todo

            if append:
                merged.append(new_match.copy())

        return merged

    def apply_transformations(
        text: str,
        transformations: List[Transformation]
    ) -> None:
        """
        This only works if matches are disjoint!!! todo
        """
        transformations.sort(key=lambda x: x.match.start)

        for transformation in transformations:
            pass

# ---------------------------------------------------------------------------- #
