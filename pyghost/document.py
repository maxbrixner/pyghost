# ---------------------------------------------------------------------------- #

import pathlib
import pdf2image
import pytesseract
import json
import logging
import importlib
from PIL import Image, ImageDraw, ImageFont
from typing import Any, List, Optional

from .models import Config
from .ocr import BaseOcr, OcrResult
from .transformers import TransformerResult

# ---------------------------------------------------------------------------- #

# todo: intiitialize ocr-Provider, logger and so on once...abs
# then provide load_document for batch processing


class Document():
    """
    The Document class reads images or PDF documents (which will be converted
    to images), calls OCR providers and applies manipulations to the images
    before exporting them.
    """
    images: List[Image.Image]
    ocr: List[OcrResult]
    _config: Config
    _logger: logging.Logger
    language: str
    ocr_provider: BaseOcr

    def __init__(
        self,
        language: str,
        config: Config,
        ocr_provider: Optional[str] = None
    ):
        self.images = []
        self.ocr = []

        self._config = config
        self._logger = logging.getLogger("pyghost.document")

        self.language = language

        ocr_provider = self._initialize_ocr(provider=ocr_provider)

    def get_text(self) -> List[str]:
        result = []
        for page, ocr in enumerate(self.ocr):
            result.append(
                ocr.text
            )
        return result

    def load(self, filename: pathlib.Path) -> None:
        if not filename.is_file():
            raise Exception(f"Cannot find file '{filename}'.")

        if filename.suffix.lower() not in \
                [".jpg", ".jpeg", ".png", ".tiff", ".pdf"]:
            raise Exception(f"Invalid file extension '{filename.suffix}'.")

        if filename.suffix.lower() == ".pdf":
            self._load_pdf(filename=filename)
        else:
            self._load_image(filename=filename)

        self._retrieve_ocr()

    def _load_pdf(self, filename: pathlib.Path) -> None:
        self.images = pdf2image.convert_from_path(filename)
        try:
            self.images = pdf2image.convert_from_path(filename)
        except:
            raise Exception(f"Unable to convert "
                            f"'{filename.suffix}' to an image.")

    def _load_image(self, filename: pathlib.Path) -> None:
        try:
            image = Image.open(filename)
            self.images = [image]
        except:
            raise Exception(f"Unable to open image file "
                            f"'{filename.suffix}'.")

    def _retrieve_ocr(self, provider: Optional[str] = None) -> OcrResult:
        self.ocr = []

        for page, image in enumerate(self.images):
            result = self.ocr_provider.process_image(
                image=image,
                page_increment=page
            )
            self.ocr.append(result)

    def _initialize_ocr(self, provider: Optional[str] = None) -> None:
        """
        Intitialize an ocr provider. The first active provider that fits
        the language, will be used.
        """
        for ocr in self._config.ocr:
            if provider and provider == ocr.name:
                self._logger.debug(
                    f"Initializing ocr provider '{ocr.name}'.")

                module = importlib.import_module(ocr.module)
                cls = getattr(module, ocr.cls)

                self.ocr_provider = cls(config=ocr.config)
                return

            if self.language not in ocr.languages:
                continue

            if not provider:
                self._logger.warning(
                    f"No OCR provider specified, defaulting to '{ocr.name}'."
                )

                module = importlib.import_module(ocr.module)
                cls = getattr(module, ocr.cls)

                self.ocr_provider = cls(config=ocr.config)
                return

        raise Exception(
            f"No suitable OCR provider for language '{self.language}' found. "
            f" Please check your configuration.")

    def manipulate_page(
        self,
        page: int,
        transformer: TransformerResult
    ) -> None:
        draw = ImageDraw.Draw(self.images[page])

        for word in self.ocr[page].words:
            for transformation in transformer.transformations:
                if transformation.match.ignore:
                    continue

                # check here if word overlaps with transformation

                self.draw_rectangle(
                    draw=draw,
                    left=word.coordinates.left,
                    top=word.coordinates.top,
                    width=word.coordinates.width,
                    height=word.coordinates.height
                )

        self.images[page].save("output.jpg")

    def draw_rectangle(
        self,
        draw: ImageDraw.Draw,
        left: int,
        top: int,
        width: int,
        height: int,
        color: str = "#000000"
    ) -> None:
        draw.rectangle(
            [
                (left, top),
                (left+width, top+height)
            ],
            fill=color)

# ---------------------------------------------------------------------------- #
