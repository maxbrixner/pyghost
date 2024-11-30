# ---------------------------------------------------------------------------- #

import pathlib
import json
import logging
import importlib
from typing import List

# ---------------------------------------------------------------------------- #

from .models import Config
from .matchers import BaseMatcher
from .transformers import BaseTransformer
from .matchers import Match

# ---------------------------------------------------------------------------- #


class Pseudomizer():
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

    def __init__(
        self,
        configfile: pathlib.Path = pathlib.Path("config.json")
    ):
        """
        Initialize the Pseudomizer.
        """
        self._config = self._load_config(configfile=configfile)
        self._logger = logging.getLogger("pyghost")

        self._matchers = {}
        self._transformers = {}

        self._initialize_matchers()
        self._initialize_transformers()

    def process(self, text: str) -> List[Match]:
        """
        Process a text, i.e. find matches and transform them.
        """
        matches = []
        for name, matcher in self._matchers.items():
            self._logger.debug(f"Processing matcher '{name}'.")

            new_matches = matcher.process(text=text)
            for match in new_matches:
                match.label = name
            matches += new_matches

            self._logger.debug(f"Found {len(new_matches)} matches.")

        # self._export_matches(matches, pathlib.Path("test_match_export.json"))

        for name, transformer in self._transformers.items():
            self._logger.debug(f"Processing transformer '{name}'.")

            transformer.process(text=text, matches=matches)

        return matches

    def _export_matches(
        self,
        matches: List[Match],
        filename: pathlib.Path
    ) -> None:
        """
        Save all matches to a json file.
        """
        with filename.open("w") as file:
            content = [match.dict() for match in matches]
            json.dump(content, file, indent=4)

    def _load_config(self, configfile: pathlib.Path) -> Config:
        """
        Load the configuration from a config file.
        """
        with configfile.open("r") as file:
            content = json.load(file)

        return Config(**content)

    def _initialize_matchers(self) -> None:
        """
        Intitialize all active matchers once. 
        """
        self._matchers = {}

        for matcher in self._config.matchers:
            if matcher.name in self._matchers:
                raise Exception(f"Matcher name '{
                                matcher.name}' is not unique.")

            if not matcher.active:
                continue

            self._logger.debug(
                f"Initializing matcher '{matcher.name}' "
                f"as '{matcher.cls}'.")

            module = importlib.import_module(matcher.module)
            cls = getattr(module, matcher.cls)
            self._matchers[matcher.name] = cls(config=matcher.config)

    def _initialize_transformers(self) -> None:
        """
        Intitialize all active transformers once. 
        """
        self._transformers = {}

        for transformer in self._config.transformers:
            if transformer.name in self._transformers:
                raise Exception(f"Transformer name '{
                                transformer.name}' is not unique.")

            if not transformer.active:
                continue

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
