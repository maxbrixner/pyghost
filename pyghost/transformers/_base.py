
# ---------------------------------------------------------------------------- #

import pydantic
import logging
from typing import Any, List, Optional

# ---------------------------------------------------------------------------- #

from ..models import Match, Transformation, TransformerResult, Word

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

    def get_suffix(self, text: str) -> (str, str):
        """
        Return a text and it's suffix as a tuple, e.g. the text "John." will
        be returned as ("John", ".").
        """
        for suffix in [',', '.', '!', '?', ';']:
            if text.endswith(suffix):
                return (text[:len(text)-1], suffix)

        return (text, "")

    def add_to_memory(
        self,
        label: str,
        text: str,
        replacement: str
    ) -> None:
        """
        Add a text belonging to a certain label to memory.
        """
        if label not in self.memory:
            self.memory[label] = {}
        self.memory[label][text] = replacement

    def from_memory(self, label: str, text: str) -> str | None:
        """
        Retrieve a text belonging to a certain label from memory.
        """
        if label in self.memory:
            if text in self.memory[label]:
                return self.memory[label][text]

        return None

    def merge_overlapping_matches2(self, matches: List[Match]) -> List[Match]:
        """
        Merge overlapping matches.
        """
        for index, match in enumerate(matches):
            for prev_index, prev_match in enumerate(matches):

                # only check previous matches
                if prev_index >= index or prev_match.ignore:
                    continue

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

    def merge2(self, match1: Match, match2: Match) -> Match:
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

    def apply_transformations2(
        self,
        text: str,
        transformations: List[Transformation]
    ) -> str:
        """
        Apply a list of transformations to a text. The mathematical function
        that determines the new positions relative to the transformed text is
        encoded in a transformation matrix.
        """
        # Interpretation of the transformation matrix: the keys are the
        # positions of the letters in the original text. The values are the new
        # positions of these letters now. A value of None means that the letter
        # that was present at this specific position, does no longer exist
        # (i.e. has been removed or been replaced)
        trafo_matrix: dict[int, int | None] = dict(
            zip(range(0, len(text)+1), range(0, len(text)+1))
        )

        for transformation in transformations:
            # if transformation.match.ignore:
            #    continue

            self.logger.debug(f"Applying transformation to "
                              f"'{transformation.word.text}'.")

            text_orig = transformation.word.text
            start_orig = transformation.word.start
            end_orig = transformation.word.end
            len_orig = len(text_orig)
            start_orig_tf = trafo_matrix[transformation.word.start]
            end_orig_tf = trafo_matrix[transformation.word.end]

            text_new = transformation.replacement
            len_new = len(text_new)

            # if any of the letters of the original text have been already
            # replaced, the transformation cannot be applied.
            for pos in range(start_orig, end_orig):
                if trafo_matrix[pos] is None:
                    raise Exception(f"Match positions are not disjoint. The "
                                    f"transformation of '{text_orig}' "
                                    f"at {pos} "
                                    f"could not be applied.")

            # replace the text
            left = text[0:start_orig_tf]
            right = text[end_orig_tf:]
            text = left + text_new + right

            # Update the transformation matrix, i.e. replace any position with
            # a replaced letter with None and move letters after the
            # replacement by the difference of length between the new and old
            # text
            for pos_orig, pos_new in trafo_matrix.items():
                if pos_orig >= start_orig and pos_orig < end_orig:
                    trafo_matrix[pos_orig] = None

                if pos_orig >= end_orig:
                    if trafo_matrix[pos_orig] is not None:
                        trafo_matrix[pos_orig] += (len_new - len_orig)

        return text

    def apply_transformations(
        self,
        text: str,
        transformations: List[Transformation]
    ) -> str:
        """
        Apply a list of transformations to a text. The mathematical function
        that determines the new positions relative to the transformed text is
        encoded in a transformation matrix.
        """
        # Interpretation of the transformation matrix: the keys are the
        # positions of the letters in the original text. The values are the new
        # positions of these letters now. A value of None means that the letter
        # that was present at this specific position, does no longer exist
        # (i.e. has been removed or been replaced)
        trafo_matrix: dict[int, int | None] = dict(
            zip(range(0, len(text)+1), range(0, len(text)+1))
        )

        for transformation in transformations:
            # if transformation.match.ignore:
            #    continue

            self.logger.debug(f"Applying transformation to "
                              f"'{transformation.word.text}'.")

            text_orig = transformation.word.text
            start_orig = transformation.word.start
            end_orig = transformation.word.end
            len_orig = len(text_orig)
            start_orig_tf = trafo_matrix[transformation.word.start]
            end_orig_tf = trafo_matrix[transformation.word.end]

            text_new = transformation.replacement
            len_new = len(text_new)

            # if any of the letters of the original text have been already
            # replaced, the transformation cannot be applied.
            for pos in range(start_orig, end_orig):
                if trafo_matrix[pos] is None:
                    raise Exception(f"Match positions are not disjoint. The "
                                    f"transformation of '{text_orig}' "
                                    f"at {pos} "
                                    f"could not be applied.")

            # replace the text
            left = text[0:start_orig_tf]
            right = text[end_orig_tf:]
            text = left + text_new + right

            # Update the transformation matrix, i.e. replace any position with
            # a replaced letter with None and move letters after the
            # replacement by the difference of length between the new and old
            # text
            for pos_orig, pos_new in trafo_matrix.items():
                if pos_orig >= start_orig and pos_orig < end_orig:
                    trafo_matrix[pos_orig] = None

                if pos_orig >= end_orig:
                    if trafo_matrix[pos_orig] is not None:
                        trafo_matrix[pos_orig] += (len_new - len_orig)

        return text

    def debug_print2(self, trafo_matrix, old_text, text):
        keys = list(trafo_matrix.keys())
        values = list(trafo_matrix.values())
        for i in range(len(old_text)):
            key = keys[i]
            value = values[i]
            old = old_text[i]
            new = text[values[i]] if values[i] is not None else None
            print(f"{key} {value} {old} {new}")

# ---------------------------------------------------------------------------- #
