
# ---------------------------------------------------------------------------- #

import pydantic
import logging
from typing import Any, List, Optional, Tuple

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

    def process(
        self,
        text: str,
        matches: List[Match],
        words: List[Word]
    ) -> TransformerResult:
        """
        Merge overlappig transformations, call create_transformations and apply
        them to the text. Only overwrite this in special cases.
        """
        transformations = self.create_transformations(matches=matches)

        transformed_text = self.apply_transformations(
            text=text,
            transformations=transformations,
            words=words
        )

        return TransformerResult(
            source_text=text,
            transformed_text=transformed_text,
            transformations=transformations
        )

    def get_suffix(self, text: str) -> Tuple[str, str]:
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

    def apply_transformations(
        self,
        text: str,
        transformations: List[Transformation],
        words: List[Word]
    ) -> str:
        """
        Apply a list of transformations to a text.
        """
        text = ""
        for word in words:
            if len(text) > 0:
                text += " "

            transformed = False
            for transformation in transformations:
                if transformation.word != word:
                    # this will skip already transformed words, since
                    # then the original word will have changed
                    continue

                self.logger.debug(f"Applying transformation "
                                  f"'{transformation.replacement}' "
                                  f"to word '{word.text}'.")

                word.text = transformation.replacement

                text += transformation.replacement
                transformation.applied = True
                transformed = True

            if not transformed:
                text += word.text

        return text

# ---------------------------------------------------------------------------- #
