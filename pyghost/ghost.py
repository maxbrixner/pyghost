# ---------------------------------------------------------------------------- #

import logging
import importlib
from typing import List, Optional, Tuple

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

        self.language = language

        self._initialize_matchers()
        self._initialize_transformer(provider=transformer)

    def process_text(
        self,
        text: str,
        words: List[Word]
    ) -> Tuple[List[Match], TransformerResult]:
        """
        Process a text by using the matchers to find sensitive information and
        the transformers to replace it.
        """
        matches = self._find_matches(text=text, words=words)
        transformation = self._transform_text(
            text=text, matches=matches, words=words)

        return (matches, transformation)

    def _find_matches(
        self,
        text: str,
        words: List[Word]
    ) -> List[Match]:
        """
        Find matches in a text using all the configured matchers.
        """
        matches = []
        for name, matcher in self.matchers.items():
            new_matches = matcher.process(text=text)
            matches += new_matches

            self.logger.debug(
                f"Matcher '{name}' found {len(new_matches)} matches.")

        self._get_touched_words(matches=matches, words=words)

        return matches

    def _transform_text(
        self,
        text: str,
        matches: List[Match],
        words: List[Word]
    ) -> TransformerResult:
        """
        Call the transformer to replace matches with dummy data.
        """
        result = self.transformer.process(
            text=text, matches=matches, words=words)

        return result

    def _get_touched_words(
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

            self.logger.debug(f"Match '{match.text}' @ {match.start} touched "
                              f"'{len(match.touched)}' words.")

    def _initialize_matchers(self) -> None:
        """
        Intitialize all active matchers once. 
        """
        self.matchers = {}

        self.logger.debug(
            f"Initializing matchers for language '{self.language}'.")

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

    def _initialize_transformer(self, provider: Optional[str] = None) -> None:
        """
        Intitialize the transformer. If no provider is passed, the first
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
