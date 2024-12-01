
# ---------------------------------------------------------------------------- #

import pydantic
import logging
from typing import Any, List, Optional

# ---------------------------------------------------------------------------- #

from ..matchers import Match

# ---------------------------------------------------------------------------- #


class Transformation(pydantic.BaseModel):
    """
    This should not be overwritten or extended.
    """
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

    memory: dict[str, dict[str, str]]

    def __init__(
        self,
        config: dict[Any, Any]
    ):
        """
        Initialize the transformer and assign the configuration.
        """
        self.config = self.TransformerConfig(**config)
        self.logger = logging.getLogger("pyghost.transformers")
        self.memory = {}

    def create_transformations(
        self,
        matches: List[Match]
    ) -> List[Transformation]:
        """
        Overwrite this method to implement your transformer's processing.
        """
        return []

    def process(self, text: str, matches: List[Match]) -> TransformerResult:
        """
        Merge overlappig transformations, call create_transformations and apply
        them to the text. Only overwrite this in special cases.
        """
        merged_matches = self.merge_overlapping_matches(matches)

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

    def add_to_memory(
        self,
        label: str,
        text: str,
        replacement: str
    ) -> None:
        """
        Add a text belonging to a certain label to memory.
        """
        self.memory[label] = {text: replacement}

    def from_memory(self, label: str, text: str) -> str | None:
        """
        Retrieve a text belonging to a certain label from memory.
        """
        if label in self.memory:
            if text in self.memory[label]:
                return self.memory[label][text]

        return None

    def merge_overlapping_matches(self, matches: List[Match]) -> List[Match]:
        """
        Merge overlapping matches.
        """
        for index, match in enumerate(matches):
            for prev_index, prev_match in enumerate(matches):

                # only check previous matches
                if prev_index >= index or prev_match.ignore:
                    break

                # match is a subset of the previous match:
                # previous match dominates
                if match.start >= prev_match.start \
                        and match.end <= prev_match.end:
                    self.logger.debug(
                        f"Match '{match.text}' is subset of match "
                        f"'{prev_match.text}'. Will skip.")
                    match.ignore = True
                    continue

                # match is a superset of the previous match:
                # previous match dominates
                if match.start <= prev_match.start \
                        and match.end >= prev_match.end:
                    self.logger.debug(
                        f"Match '{match.text}' is real superset of match "
                        f"'{prev_match.text}'. Will replace.")
                    match.ignore = True
                    continue

                # match overlaps previous match
                # merge the two matches
                if (match.start < prev_match.start
                        and match.end < prev_match.end
                        and match.end > prev_match.start) or \
                   (match.start > prev_match.start
                        and match.start < prev_match.end
                        and match.end > prev_match.end):
                    self.logger.debug(
                        f"Match '{match.text}' overlaps with match "
                        f"'{prev_match.text}'. Will merge.")
                    match.ignore = True
                    prev_match.ignore = True

                    merged = self.merge(match, prev_match)

                    matches.append(merged)

        return matches

    def merge(self, match1: Match, match2: Match) -> Match:
        """
        Merge two matches by combining their start end end positions and
        their text. Merged matches will have merged=True. If the two
        matches had the same label, the merged match will have the same label.
        Otherwise it will have the label "multiple".
        """
        start = min(match1.start, match2.start)
        end = max(match1.end, match2.end)

        if match1.label == match2.label:
            label = match1.label
        else:
            label = "multiple"

        if match1.start <= match2.start:
            left = match1.text
        else:
            left = match2.text

        if match1.end >= match2.end:
            right = match1.text[(max(match1.start, match2.end)-match1.start):]
        else:
            right = match2.text[(max(match2.start, match1.end)-match2.start):]

        return Match(
            start=start,
            end=end,
            text=left+right,
            label=label,
            merged=True
        )

    def apply_transformations(
        self,
        text: str,
        transformations: List[Transformation]
    ) -> str:
        """
        todo
        """

        # the trafo matrix says: for every letter from the original text: where is it now?
        trafo_matrix: dict[int, int | None] = dict(
            zip(range(0, len(text)+1), range(0, len(text)+1))
        )

        old_text = text

        for transformation in transformations:
            if transformation.match.ignore:
                continue

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
                    "Match positions are not disjoint.")
                continue

            abort = False
            for pos in range(start_orig, end_orig):
                if trafo_matrix[pos] is None:
                    self.logger.warning(
                        "Match positions are not disjoint.")
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
