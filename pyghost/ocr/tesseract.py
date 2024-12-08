# ---------------------------------------------------------------------------- #

import pydantic
import pytesseract
from PIL import Image
from typing import List

# ---------------------------------------------------------------------------- #

from ._base import BaseOcr
from ..models import OcrResult, Word, Coordinates

# ---------------------------------------------------------------------------- #


class TesseractOcr(BaseOcr):

    class OcrConfig(pydantic.BaseModel):
        """
        Use this pydantic model to define your matcher's config
        parameters.
        """
        lang: str

    class TesseractResult(pydantic.BaseModel):
        level: List[int]
        page_num: List[int]
        block_num: List[int]
        par_num: List[int]
        line_num: List[int]
        word_num: List[int]
        left: List[int]
        top: List[int]
        width: List[int]
        height: List[int]
        conf: List[int]
        text: List[str]

    def process_image(
        self,
        image: Image.Image,
        page_increment: int = 0
    ) -> OcrResult:
        assert isinstance(self.config, self.OcrConfig)

        boxes = pytesseract.image_to_data(
            image, output_type=pytesseract.Output.DICT, lang=self.config.lang)

        result = self.TesseractResult(**boxes)

        words = []
        doc_text = ""
        start = 0
        end = 0
        for index, text in enumerate(result.text):

            if len(text) == 0:
                continue

            if len(doc_text):
                doc_text += " "
                start += 1

            doc_text += text
            end = start+len(text)

            words.append(
                Word(
                    text=text,
                    start=start,
                    end=end,
                    page=result.page_num[index]+page_increment,
                    coordinates=Coordinates(
                        left=result.left[index],
                        top=result.top[index],
                        width=result.width[index],
                        height=result.height[index]
                    )
                )
            )

            start += len(text)

        ocr = OcrResult(
            text=doc_text,
            words=words
        )

        return ocr

# ---------------------------------------------------------------------------- #
