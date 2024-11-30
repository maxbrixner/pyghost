# ---------------------------------------------------------------------------- #

import pydantic
import re
from typing import Any, List, Optional

# ---------------------------------------------------------------------------- #

from ._base import BaseMatcher, Match

# ---------------------------------------------------------------------------- #


class PatternConfig(pydantic.BaseModel):
    pattern: str
    group: int
    compiled: Optional[re.Pattern] = None

# ---------------------------------------------------------------------------- #


class RegexMatcher(BaseMatcher):
    """
    The RegexMatcher uses regular expressions to identify entities.
    """
    class MatcherConfig(pydantic.BaseModel):
        patterns: List[str | PatternConfig] = []
        patterns_file: Optional[str] = None  # todo

    compiled_patterns: List[PatternConfig]

    def __init__(
        self,
        label: str,
        config: dict[Any, Any]
    ) -> None:
        """
        Initialize the RegexMatcher.
        """
        super().__init__(label=label, config=config)

        self._compile_patterns()

    def _compile_patterns(self) -> None:
        """
        Precompile regex patterns for faster processing.
        """
        self.logger.debug(
            f"Compiling {len(self.config.patterns)} regex patterns.")

        self.compiled_patterns = []
        for pattern in self.config.patterns:
            if isinstance(pattern, str):
                pattern = PatternConfig(
                    pattern=pattern,
                    group=0
                )

            pattern.compiled = re.compile(pattern=pattern.pattern)

            self.compiled_patterns.append(pattern)

    def process(self, text: str) -> List[Match]:
        """
        Process all patterns.
        """
        result = []
        for pattern in self.compiled_patterns:
            result += self._match_pattern(text=text, pattern=pattern)

        return result

    def _match_pattern(self, text: str, pattern: PatternConfig):
        """
        Process a single pattern and find all matches.
        """
        matches = re.finditer(pattern=pattern.pattern, string=text)

        result = []
        for match in matches:
            text = match.group(pattern.group)

            result.append(
                Match(
                    label=self.label,
                    text=text,
                    context=match.group(0),
                    start=match.start(),
                    end=match.end()
                )
            )

        return result


# ---------------------------------------------------------------------------- #
