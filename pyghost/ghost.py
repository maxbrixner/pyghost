# ---------------------------------------------------------------------------- #

import pathlib
import json
import logging
import importlib
from typing import List, Optional

# ---------------------------------------------------------------------------- #

from .models import Config, Match, TransformerResult
from .matchers import BaseMatcher
from .transformers import BaseTransformer

# ---------------------------------------------------------------------------- #


class Ghost():
    """
    The Pseudomizer processes a text by using the configured matchers to
    find entities and the configures transformers to transform those
    entities into pseudononymized or anonymized text. It tries to do that
    efficiently by initializing matchers and transformers only once.
    """
    _config: Config
    _logger: logging.Logger
    _matchers: dict[str, BaseMatcher]
    _transformer: BaseTransformer
    language: str

    def __init__(
        self,
        language: str,
        config: Config,
        transformer: Optional[str] = None
    ):
        """
        Initialize the Pseudomizer.
        """
        self._config = config
        self._logger = logging.getLogger("pyghost.ghost")

        self._matchers = {}
        self._transformer = self._initialize_transformer(
            provider=transformer)

        self.language = language

        self._initialize_matchers()

    def find_matches(self, text: str) -> List[Match]:
        """
        Process a text, i.e. find matches and transform them.
        """
        matches = []
        for name, matcher in self._matchers.items():
            self._logger.debug(f"Processing matcher '{name}'.")

            new_matches = matcher.process(text=text)
            matches += new_matches

            self._logger.debug(f"Found {len(new_matches)} matches.")

        return matches

    def transform_text(
        self,
        text: str,
        matches: List[Match]
    ) -> TransformerResult:
        result = self.transformer.process(text=text, matches=matches)

        return result

    def _initialize_matchers(self) -> None:
        """
        Intitialize all active matchers once. 
        """
        self._matchers = {}

        for matcher in self._config.matchers:
            if matcher.name in self._matchers:
                raise Exception(f"Matcher name "
                                f"'{matcher.name}' is not unique.")

            if self.language not in matcher.languages:
                continue

            self._logger.debug(
                f"Initializing matcher '{matcher.name}' "
                f"as '{matcher.cls}'.")

            module = importlib.import_module(matcher.module)
            cls = getattr(module, matcher.cls)
            self._matchers[matcher.name] = cls(
                name=matcher.name,
                label=matcher.label,
                config=matcher.config)

    def _initialize_transformer(self, provider: Optional[str] = None) -> None:
        """
        Intitialize a transformer. If no provider is passed, the first
        transformer found will be used.
        """
        for transformer in self._config.transformers:
            if provider and provider == transformer.name:
                self._logger.debug(
                    f"Initializing transformer '{transformer.name}'.")

                module = importlib.import_module(transformer.module)
                cls = getattr(module, transformer.cls)

                self.transformer = cls(config=transformer.config)
                return

            if not provider:
                self._logger.warning(
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
