# ---------------------------------------------------------------------------- #

import pydantic
import spacy
from typing import Any, List, Optional

# ---------------------------------------------------------------------------- #

from ._base import BaseMatcher
from ..models import Match

# ---------------------------------------------------------------------------- #


class SpacyCacher():

    models: dict[str, spacy.Language]

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

    model: Optional[spacy.Language] = None

    def __init__(
        self,
        label: str,
        name: str,
        config: dict[Any, Any]
    ) -> None:
        super().__init__(name=name, label=label, config=config)

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
        if self.model is None:
            raise Exception("Invalid spacy model.")

        doc = self.model(text=text)

        result = []
        for entity in doc.ents:
            if self.config.labels and entity.label_ not in self.config.labels:
                continue

            result.append(
                Match(
                    matcher=self.name,
                    label=self.label,
                    text=entity.text,
                    start=entity.start_char,
                    end=entity.end_char,
                    model_label=entity.label_
                )
            )

        return result


# ---------------------------------------------------------------------------- #
