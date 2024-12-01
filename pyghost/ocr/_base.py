# ---------------------------------------------------------------------------- #

import pydantic
import logging
from PIL import Image
from typing import Any, List

# ---------------------------------------------------------------------------- #

from ..models import OcrResult

# ---------------------------------------------------------------------------- #


class BaseOcr():

    class OcrConfig(pydantic.BaseModel):
        """
        Use this pydantic model to define your matcher's config
        parameters.
        """
        pass

    config: OcrConfig
    logger: logging.Logger

    def __init__(self, config: dict[Any, Any]) -> None:
        self.config = self.OcrConfig(**config)
        self.logger = logging.getLogger("pyghost.ocr")

    def process_image(self, image: Image.Image) -> OcrResult:
        pass

# ---------------------------------------------------------------------------- #
