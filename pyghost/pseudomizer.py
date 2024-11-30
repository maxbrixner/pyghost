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

    _config: Config
    _logger: logging.Logger
    _matchers: dict[str, BaseMatcher]
    _transformers: dict[str, BaseTransformer]

    def __init__(
        self,
        configfile: pathlib.Path = pathlib.Path("config.json")
    ):
        self._config = self._load_config(configfile=configfile)
        self._logger = logging.getLogger("pyghost")

        self._matchers = {}
        self._transformers = {}

        self._initialize_matchers()

    def process(self, text: str) -> List[Match]:
        matches = []
        for name, matcher in self._matchers.items():
            matches += matcher.process(text=text)

        return matches

    def _load_config(self, configfile: pathlib.Path) -> Config:
        with configfile.open("r") as file:
            content = json.load(file)

        return Config(**content)

    def _initialize_matchers(self) -> None:
        self._matchers = {}

        for matcher in self._config.matchers:
            if matcher.name in self._matchers:
                raise Exception(f"Matcher name '{
                                matcher.name}' is not unique.")

            self._logger.debug(
                f"Initializing matcher '{matcher.name}' as '{matcher.cls}'...")

            module = importlib.import_module(matcher.module)

            cls = getattr(module, matcher.cls)

            self._matchers[matcher.name] = cls(config=matcher.config)

# ---------------------------------------------------------------------------- #
