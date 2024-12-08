# ---------------------------------------------------------------------------- #

from typing import List

# ---------------------------------------------------------------------------- #

from .models import Word

# ---------------------------------------------------------------------------- #


class Text():

    def get_words(self, text: str) -> List[Word]:
        # todo
        # text = text.replace(".", " ")
        # text = text.replace(",", " ")
        # text = text.replace(";", " ")
        # text = text.replace("?", " ")
        # text = text.replace("!", " ")

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
