# ---------------------------------------------------------------------------- #

import pathlib
import json
import logging
import importlib
from typing import List, Optional

# ---------------------------------------------------------------------------- #

from .models import Config, TransformerConfig, MatcherConfig
from .matchers import BaseMatcher, Match
from .transformers import BaseTransformer, TransformerResult

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

    def __init__(
        self,
        config: Optional[pathlib.Path] = None
    ):
        """
        Initialize the Pseudomizer.
        """
        self._config = self._load_config(configfile=config)
        self._logger = logging.getLogger("pyghost")

        self._matchers = {}
        self._transformers = {}

        self._initialize_matchers()
        self._initialize_transformers()

    def process(self, text: str) -> TransformerResult:
        """
        Process a text, i.e. find matches and transform them.
        """
        matches = []
        for name, matcher in self._matchers.items():
            self._logger.debug(f"Processing matcher '{name}'.")

            new_matches = matcher.process(text=text)
            matches += new_matches

            self._logger.debug(f"Found {len(new_matches)} matches.")

        for name, transformer in self._transformers.items():
            self._logger.debug(f"Processing transformer '{name}'.")

            result = transformer.process(text=text, matches=matches)

        return result

    def export_result(
        self,
        result: TransformerResult,
        filename: pathlib.Path
    ) -> None:
        """
        Save all matches to a json file.
        """
        with filename.open("w") as file:
            content = result.dict()
            json.dump(content, file, indent=4)

    def _load_config(
        self,
        configfile: Optional[pathlib.Path] = None
    ) -> Config:
        """
        Load the configuration from a config file.
        """
        if not configfile:
            configfile = pathlib.Path(__file__).parent / \
                pathlib.Path("../config/default.json")

        try:
            with configfile.open("r") as file:
                content = json.load(file)

            return Config(**content)
        except:
            raise Exception(
                f"Unable to read the configuration at '{configfile}'. "
                f"You can specify another location with the --config "
                f"parameter.")

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
            self._matchers[matcher.name] = cls(
                label=matcher.label, config=matcher.config)

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
