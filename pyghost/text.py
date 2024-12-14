# ---------------------------------------------------------------------------- #

from typing import List

# ---------------------------------------------------------------------------- #

from .models import Word

# ---------------------------------------------------------------------------- #


class Text():
    """
    The text class offers a way to convert a string of text into a list of
    words.
    """

    def get_words(self, text: str) -> List[Word]:
        """
        Convert a string of text into a list of words.
        """
        words = text.split(" ")
        result = []
        start = 0
        end = 0
        for word in words:
            if len(word) == 0:
                start += 1
                continue

            end = start+len(word)

            result.append(
                Word(
                    text=word,
                    start=start,
                    end=end,
                    page=0
                )
            )

            start += (len(word) + 1)

        return result

# ---------------------------------------------------------------------------- #
