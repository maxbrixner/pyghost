# ---------------------------------------------------------------------------- #

import pydantic
import spacy
from typing import Any, List, Optional

# ---------------------------------------------------------------------------- #

from ._base import BaseMatcher, Match

# ---------------------------------------------------------------------------- #


class SpacyCacher():

    models: dict[str, spacy.language]

    def __init__(self) -> None:
        self.models = {}


cache = SpacyCacher()

# ---------------------------------------------------------------------------- #


class SpacyMatcher(BaseMatcher):
    """
    The SpacyMatcher facilitates the Spacy package to identify entities using
    natural language processing.
    """

    class MatcherConfig(pydantic.BaseModel):
        model: str
        labels: Optional[List[str]] = None

    model: Optional[spacy.language] = None

    def __init__(
        self,
        label: str,
        config: dict[Any, Any]
    ) -> None:
        super().__init__(label=label, config=config)

        self.model = None
        self._load_model()

    def _load_model(self) -> None:
        """
        Attempt to load a spacy model.
        """
        try:
            if not self.config.model in cache.models:
                self.logger.debug(
                    f"Loading spacy model '{self.config.model}'.")
                cache.models[self.config.model] = spacy.load(self.config.model)
        except:
            raise Exception(f"The spacy model '{self.config.model}' is not "
                            f"installed. Use 'python -m spacy download "
                            f"{self.config.model}' to install it")

        self.model = cache.models[self.config.model]

    def process(self, text: str) -> List[Match]:
        """
        Use spacy to identify entities.
        """
        doc = self.model(text=text)

        result = []
        for entity in doc.ents:
            if self.config.labels and entity.label_ not in self.config.labels:
                continue

            result.append(
                Match(
                    label=self.label,
                    text=entity.text,
                    start=entity.start,
                    end=entity.end,
                    source_labels=[entity.label_]
                )
            )

        return result


# ---------------------------------------------------------------------------- #


# ---------------------------------------------------------------------------- #
