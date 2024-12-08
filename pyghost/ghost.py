# ---------------------------------------------------------------------------- #

import pathlib
import json
import logging
import importlib
from typing import List, Optional

# ---------------------------------------------------------------------------- #

from .models import Config, Match, TransformerResult, Word
from .matchers import BaseMatcher
from .transformers import BaseTransformer

# ---------------------------------------------------------------------------- #


class Ghost():
    """
    The Ghost class processes a text by using the configured matchers to
    find entities and the configures transformers to transform those
    entities into pseudononymized or anonymized text. It does that efficiently
    in the sense that it iiitializes matchers and transformers only once.
    """
    config: Config
    logger: logging.Logger
    matchers: dict[str, BaseMatcher]
    transformer: BaseTransformer
    language: str

    def __init__(
        self,
        language: str,
        config: Config,
        transformer: Optional[str] = None
    ):
        """
        Initialize Ghost.
        """
        self.config = config
        self.logger = logging.getLogger("pyghost.ghost")

        self.matchers = {}

        self.language = language

        self.initialize_matchers()
        self.initialize_transformer(provider=transformer)

    def find_matches(
        self,
        text: str,
        words: List[Word]
    ) -> List[Match]:
        """
        Find matches in a text using all the configured matchers.
        """
        matches = []
        for name, matcher in self.matchers.items():
            self.logger.debug(f"Processing matcher '{name}'.")

            new_matches = matcher.process(text=text)
            matches += new_matches

            self.logger.debug(f"Found {len(new_matches)} matches.")

        self.get_touched_words(matches=matches, words=words)

        return matches

    def get_touched_words(
        self,
        matches: List[Match],
        words: List[Word]
    ) -> None:
        """
        Add all words to the match that have been "touched" by it, i.e.
        overlap with the match.
        """
        for match in matches:
            match.touched = []
            for word in words:
                if not ((word.start >= match.start
                         and word.start < match.end) or
                        (word.end > match.start
                         and word.end <= match.end)):
                    continue

                match.touched.append(word.copy())

            self.logger.debug(f"Found {len(match.touched)} touched words for "
                              f"match '{match.text}'")

    def transform_text(
        self,
        text: str,
        matches: List[Match]
    ) -> TransformerResult:
        """
        Call the transformer to #todo
        """
        result = self.transformer.process(text=text, matches=matches)

        return result

    def initialize_matchers(self) -> None:
        """
        Intitialize all active matchers once. 
        """
        self.matchers = {}

        for matcher in self.config.matchers:
            if matcher.name in self.matchers:
                raise Exception(f"Matcher name "
                                f"'{matcher.name}' is not unique.")

            if self.language not in matcher.languages:
                continue

            self.logger.debug(
                f"Initializing matcher '{matcher.name}' "
                f"as '{matcher.cls}'.")

            module = importlib.import_module(matcher.module)
            cls = getattr(module, matcher.cls)
            self.matchers[matcher.name] = cls(
                name=matcher.name,
                label=matcher.label,
                config=matcher.config)

    def initialize_transformer(self, provider: Optional[str] = None) -> None:
        """
        Intitialize a transformer. If no provider is passed, the first
        transformer found will be used.
        """
        for transformer in self.config.transformers:
            if provider and provider == transformer.name:
                self.logger.debug(
                    f"Initializing transformer '{transformer.name}'.")

                module = importlib.import_module(transformer.module)
                cls = getattr(module, transformer.cls)

                self.transformer = cls(config=transformer.config)
                return

            if not provider:
                self.logger.info(
                    f"No transformer provider specified, defaulting to "
                    f"'{transformer.name}'."
                )

                module = importlib.import_module(transformer.module)
                cls = getattr(module, transformer.cls)

                self.transformer = cls(config=transformer.config)
                return

        raise Exception(
            f"No suitable transformer found. "
            f"Please check your configuration.")

# ---------------------------------------------------------------------------- #
