
# ---------------------------------------------------------------------------- #

import pydantic
import logging
import pathlib
import random
from typing import Any, List, Optional

# ---------------------------------------------------------------------------- #

from ._base import BaseTransformer
from ..models import Match, TransformerResult, Transformation

# ---------------------------------------------------------------------------- #


class FakerTransformer(BaseTransformer):
    """
    The faker transformer replaces entities by random items from a list.
    """
    class TransformerConfig(pydantic.BaseModel):
        """
        Use this pydantic model to define your transformer's config
        parameters.
        """
        files: dict[str, str] = {}
        min_candidates: int = 10
        random_alpha: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        random_digit: str = "0123456789"
        random_preserve: str = "@ .,+-_()#\r\t\n"
        memory: bool = False

    fakes: dict[str, List[str]]

    def __init__(
        self,
        config: dict[Any, Any]
    ) -> None:
        super().__init__(config=config)

        self.fakes = {}

    def create_transformations(
        self,
        matches: List[Match]
    ) -> List[Transformation]:
        """
        Create transformations by replacing words with a random fake.
        """
        assert isinstance(self.config, self.TransformerConfig)

        transformations = []
        for match in matches:
            for index, word in enumerate(match.touched):
                (clean_text, suffix) = self.get_suffix(word.text)

                if self.config.memory:
                    replacement = self.from_memory(
                        label=match.label, text=clean_text)
                else:
                    replacement = None

                if replacement is None:
                    replacement = self.get_fake(
                        label=match.label,
                        text=clean_text)
                    self.add_to_memory(
                        label=match.label,
                        text=clean_text,
                        replacement=replacement
                    )

                transformations.append(
                    Transformation(
                        word=word,
                        replacement=f"{replacement}"
                        f"{suffix}"
                    )
                )

        return transformations

    def get_fake(self, label: str, text: str) -> str:
        assert isinstance(self.config, self.TransformerConfig)

        self.load_file(label=label)

        if label not in self.fakes:
            return self.randomize_text(text=text)

        if len(self.fakes[label]) == 0:
            return self.randomize_text(text=text)

        candidates = []
        for candidate in self.fakes[label]:
            if len(candidate) == len(text):
                candidates.append(candidate)

        if len(candidates) < self.config.min_candidates:
            return self.randomize_text(text=text)

        return random.choice(candidates)

    def load_file(self, label: str) -> None:
        assert isinstance(self.config, self.TransformerConfig)

        if label in self.fakes:
            return

        if label not in self.config.files:
            self.fakes[label] = []
            return

        filename = pathlib.Path(self.config.files[label])
        if not filename.is_file():
            filename = pathlib.Path(__file__).parent / \
                pathlib.Path(self.config.files[label])

        self.logger.debug(f"Loading faker file '{filename}'...")

        with filename.open("r") as file:
            self.fakes[label] = file.read().splitlines()

    def randomize_text(self, text: str) -> str:
        """
        Randomize a string by replacing every character by a random character
        from a given set.
        """
        assert isinstance(self.config, self.TransformerConfig)

        result = ""
        for char in text:
            if char in self.config.random_preserve:
                result += char
                continue

            if char.isdigit():
                result += random.choice(self.config.random_digit)
            else:
                if char.islower():
                    result += random.choice(self.config.random_alpha).lower()
                else:
                    result += random.choice(self.config.random_alpha).upper()
                continue

        return result

# ---------------------------------------------------------------------------- #
