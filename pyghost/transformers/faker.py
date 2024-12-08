
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
        default: str = "*"
        min_candidates: int = 10
        allow_length_diff: bool = False
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
        self.load_file(label=label)

        if len(self.fakes[label]) == 0:
            return self.config.default

        candidates = []
        for candidate in self.fakes[label]:
            if len(candidate) == len(text):
                candidates.append(candidate)

        if len(candidates) < self.config.min_candidates:
            if not self.config.allow_length_diff:
                return self.config.default
            return random.choice(self.fakes[label])

        return random.choice(candidates)

    def load_file(self, label: str) -> None:
        if label in self.fakes:
            return

        if label not in self.config.files:
            self.fakes[label] = []
            return

        # todo: check if file exists and manipulate path
        # to point to this dir if not
        filename = pathlib.Path(self.config.files[label])

        self.logger.debug(f"Loading faker file '{filename}'...")

        with filename.open("r") as file:
            self.fakes[label] = file.read().splitlines()

# ---------------------------------------------------------------------------- #
