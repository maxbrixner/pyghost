import pytesseract
from PIL import Image
from typing import List

from ._base import BaseOcr, Word


class TesseractOcr(BaseOcr):
    pass

    def process_image(self, image: Image.Image) -> List[Word]:
        boxes = pytesseract.image_to_data(
            image, output_type=pytesseract.Output.DICT, lang="eng")

        print(boxes)
