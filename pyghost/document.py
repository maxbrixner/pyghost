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
from .ocr import BaseOcr

# ---------------------------------------------------------------------------- #


class Document():

    images: List[Image.Image]
    config: Config
    logger: logging.Logger

    def __init__(
        self,
        filename: pathlib.Path,
        config: Config
    ):
        self._config = config
        self._logger = logging.getLogger("pyghost.document")

        self.load_document(filename=filename)

        self.get_ocr()

    def load_document(self, filename: pathlib.Path) -> None:
        if not filename.is_file():
            raise Exception(f"Cannot find file '{filename}'.")

        if filename.suffix.lower() not in \
                [".jpg", ".jpeg", ".png", ".tiff", ".pdf"]:
            raise Exception(f"Invalid file extension '{filename.suffix}'.")

        if filename.suffix.lower() == ".pdf":
            self.load_pdf(filename=filename)
        else:
            self.load_image(filename=filename)

    def load_pdf(self, filename: pathlib.Path) -> None:
        self.images = pdf2image.convert_from_path(filename)
        try:
            self.images = pdf2image.convert_from_path(filename)
        except:
            raise Exception(f"Unable to convert "
                            f"'{filename.suffix}' to an image.")

    def load_image(self, filename: pathlib.Path) -> None:
        try:
            image = Image.open(filename)
            self.images = [image]
        except:
            raise Exception(f"Unable to open image file "
                            f"'{filename.suffix}'.")

    def get_ocr(self) -> None:
        ocr = self._initialize_ocr()

        ocr.process_image(self.images[0])  # todo

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
