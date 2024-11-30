
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
        self,
        text: str,
        transformations: List[Transformation]
    ) -> str:
        """
        todo
        """

        # the trafo matrix says: for every letter from the original text: where is it now?
        trafo_matrix = dict(
            zip(range(0, len(text)+1), range(0, len(text)+1))
        )

        old_text = text

        for transformation in transformations:

            text_orig = transformation.match.text
            start_orig = transformation.match.start
            end_orig = transformation.match.end
            len_orig = len(text_orig)
            start_orig_tf = trafo_matrix[transformation.match.start]
            end_orig_tf = trafo_matrix[transformation.match.end]

            text_new = transformation.replacement
            len_new = len(text_new)

            # print("text_orig", text_orig)
            # print("text_new", text_new)
            # print("start_orig", start_orig)
            # print("end_orig", end_orig)
            # print("len_orig", len_orig)
            # print("start_orig_tf", start_orig_tf)
            # print("end_orig_tf", end_orig_tf)
            # print("len_new", len_new)

            if start_orig_tf is None or end_orig_tf is None:
                self.logger.warning(
                    "Trying to manipulate already replaced text1")
                print("")
                continue

            abort = False
            for pos in range(start_orig, end_orig):
                if trafo_matrix[pos] is None:
                    self.logger.warning(
                        "Trying to manipulate already replaced text2")
                    abort = True
                    break

            if abort:
                # print("")
                continue

            before = text[0:start_orig_tf]
            after = text[end_orig_tf:]
            text = before + text_new + after

            # print(text)
            # print(old_text)

            for pos_orig, pos_new in trafo_matrix.items():
                if pos_orig >= start_orig_tf and pos_orig < end_orig_tf:
                    trafo_matrix[pos_orig] = None

                if pos_orig >= end_orig_tf:
                    if trafo_matrix[pos_orig] is not None:
                        trafo_matrix[pos_orig] += (len_new - len_orig)

            # print(trafo_matrix)

            # print("")

        return text

# ---------------------------------------------------------------------------- #
