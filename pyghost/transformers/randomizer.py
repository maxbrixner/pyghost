
# ---------------------------------------------------------------------------- #

import pydantic
import logging
import random
from typing import Any, List, Optional

# ---------------------------------------------------------------------------- #

from ._base import BaseTransformer
from ..models import Match, TransformerResult, Transformation

# ---------------------------------------------------------------------------- #


class RandomizerTransformer(BaseTransformer):
    """
    The randomizer transformer replaces entities by random strings of the
    same length while preserving some structural integrity.
    """
    class TransformerConfig(pydantic.BaseModel):
        """
        Use this pydantic model to define your transformer's config
        parameters.
        """
        alpha: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        digit: str = "0123456789"
        preserve: str = "@ .,+-_()#\r\t\n"
        memory: bool = False

    def __init__(self, config: dict[Any, Any]) -> None:
        """
        Initialize the label transformer.
        """
        super().__init__(config=config)

    def create_transformations(
        self,
        matches: List[Match]
    ) -> List[Transformation]:
        """
        Create transformations by replacing matches with their respective
        labels. If memory is active, labels will be counted to give same
        entities the same labels.
        """
        transformations = []
        for match in matches:
            for word in match.touched:
                replacement = self.from_memory(
                    label=match.label, text=word.text)

                if replacement is None:
                    replacement = self.randomize_text(word.text)
                    self.add_to_memory(
                        label=match.label,
                        text=word.text,
                        replacement=replacement
                    )

                transformations.append(
                    Transformation(
                        word=word,
                        replacement=replacement
                    )
                )

        print("mmmmmm", self.memory)

        return transformations

    def randomize_text(self, text: str) -> str:
        """
        Randomize a string by replacing every character by a random character
        from a set.
        """
        result = ""
        for char in text:
            if char in self.config.preserve:
                result += char
                continue

            if char.isalpha():
                if char.islower():
                    result += random.choice(self.config.alpha).lower()
                else:
                    result += random.choice(self.config.alpha).upper()
                continue

            if char.isdigit():
                result += random.choice(self.config.digit)

        return result

# ---------------------------------------------------------------------------- #
