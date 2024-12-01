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

# ---------------------------------------------------------------------------- #


class Document():

    images: List[Image.Image]
    ocr: List[OcrResult]
    config: Config
    logger: logging.Logger

    def __init__(
        self,
        filename: pathlib.Path,
        config: Config
    ):
        self._config = config
        self._logger = logging.getLogger("pyghost.document")

        self._load_document(filename=filename)

        self._retrieve_ocr()

    def get_text(self) -> List[str]:
        result = []
        for page, ocr in enumerate(self.ocr):
            result.append(
                ocr.text
            )
        return result

    def _load_document(self, filename: pathlib.Path) -> None:
        if not filename.is_file():
            raise Exception(f"Cannot find file '{filename}'.")

        if filename.suffix.lower() not in \
                [".jpg", ".jpeg", ".png", ".tiff", ".pdf"]:
            raise Exception(f"Invalid file extension '{filename.suffix}'.")

        if filename.suffix.lower() == ".pdf":
            self._load_pdf(filename=filename)
        else:
            self._load_image(filename=filename)

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

    def _retrieve_ocr(self) -> OcrResult:
        self.ocr = []
        ocr = self._initialize_ocr()

        for page, image in enumerate(self.images):
            result = ocr.process_image(
                image=image,
                page_increment=page
            )
            self.ocr.append(result)

    def _initialize_ocr(self) -> BaseOcr:
        """
        Intitialize an ocr provider. The first active provider will be used.
        """
        for ocr in self._config.ocr:
            if not ocr.active:
                continue

            self._logger.debug(
                f"Initializing ocr provider '{ocr.name}'.")

            module = importlib.import_module(ocr.module)
            cls = getattr(module, ocr.cls)

            return cls(config=ocr.config)

# ---------------------------------------------------------------------------- #
