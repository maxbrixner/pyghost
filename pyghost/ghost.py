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
    _transformers: dict[str, BaseTransformer]
    language: str

    def __init__(
        self,
        language: str,
        config: Config
    ):
        """
        Initialize the Pseudomizer.
        """
        self._config = config
        self._logger = logging.getLogger("pyghost.ghost")

        self._matchers = {}
        self._transformers = {}

        self.language = language

        self._initialize_matchers()
        self._initialize_transformers()  # todo: rather choose transformer

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

        for name, transformer in self._transformers.items():
            self._logger.debug(f"Processing transformer '{name}'.")

            result = transformer.process(text=text, matches=matches)

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

    # todo: do this more like ocr initialization
    def _initialize_transformers(self) -> None:
        """
        Intitialize all active transformers once. 
        """
        self._transformers = {}

        for transformer in self._config.transformers:
            if transformer.name in self._transformers:
                raise Exception(f"Transformer name "
                                f"'{transformer.name}' is not unique.")

            if len(self._transformers) > 0:
                raise Exception(f"Only one transformer can be active "
                                f"at the same time. You can activate and "
                                f"deactivate controlers by setting active="
                                f"true/false in the configuration.")

            self._logger.debug(
                f"Initializing transformer '{transformer.name}' "
                f"as '{transformer.cls}'.")

            module = importlib.import_module(transformer.module)
            cls = getattr(module, transformer.cls)
            self._transformers[transformer.name] = cls(
                config=transformer.config)

# ---------------------------------------------------------------------------- #
