# ---------------------------------------------------------------------------- #

import typer
import logging
import enum
import sys
import pathlib
import json
import pydantic
from typing import Any, Optional, List

# ---------------------------------------------------------------------------- #

from .ghost import Ghost
from .document import Document
from .models import Config

# ---------------------------------------------------------------------------- #

app = typer.Typer()

# ---------------------------------------------------------------------------- #


class LogLevel(str, enum.Enum):
    NOTSET = "NOTSET"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

# ---------------------------------------------------------------------------- #


def setup_logging(level: LogLevel) -> None:
    """
    Setup the logger for pyghost.
    """

    formatter = logging.Formatter("%(levelname)-10s %(message)s")

    handler = logging.StreamHandler()
    handler.setLevel(level.name)
    handler.setFormatter(formatter)

    logger = logging.getLogger("pyghost")
    logger.setLevel(level.name)
    logger.addHandler(handler)

# ---------------------------------------------------------------------------- #


def load_config(
    configfile: Optional[pathlib.Path] = None
) -> Config:
    """
    Load the configuration from a config file.
    """
    if not configfile:
        configfile = pathlib.Path(__file__).parent / \
            pathlib.Path("./config/default.json")

    try:
        with configfile.open("r", encoding="utf-8") as file:
            content = json.load(file)

        return Config(**content)
    except:
        raise Exception(
            f"Unable to read the configuration at '{configfile}'. "
            f"You can specify another location with the --config "
            f"parameter.")

# ---------------------------------------------------------------------------- #


def export_to_json(
    object: pydantic.BaseModel,
    filename: pathlib.Path,
    suffix: Optional[str] = None
) -> None:
    """
    Save a pydantic model to a json file.
    """
    if suffix:
        filename = filename.with_stem(f"{filename.stem}{suffix}")
    with filename.open("w", encoding="utf-8") as file:
        content = object.model_dump()
        json.dump(content, file, indent=4)

# ---------------------------------------------------------------------------- #


@app.command()
def text(
    language: str,
    text: str,
    log: LogLevel = LogLevel.INFO,
    config: Optional[pathlib.Path] = None,
    export: Optional[pathlib.Path] = None,
    transformer: Optional[str] = None
) -> None:
    """
    Pseudonymize or anonymize a text.
    """
    setup_logging(level=log)
    config = load_config(configfile=config)

    ghost = Ghost(
        language=language,
        config=config,
        transformer=transformer
    )

    matches = ghost.find_matches(text=text)

    result = ghost.transform_text(text=text, matches=matches)

    if export:
        export_to_json(
            object=result,
            filename=export
        )

    print(result.transformed_text)

# ---------------------------------------------------------------------------- #


@app.command()
def doc(
    language: str,
    documents: List[pathlib.Path],
    log: LogLevel = LogLevel.INFO,
    config: Optional[pathlib.Path] = None,
    export: Optional[pathlib.Path] = None,
    ocr: Optional[str] = None,
    transformer: Optional[str] = None
) -> None:
    """
    Process a local document (pdf, jpg, png, or tiff).
    """
    setup_logging(level=log)
    config = load_config(configfile=config)

    ghost = Ghost(
        language=language,
        config=config,
        transformer=transformer
    )

    doc = Document(
        language=language,
        config=config,
        ocr_provider=ocr
    )

    for document in documents:
        doc.load(document)

        for page, text in enumerate(doc.get_text()):
            matches = ghost.find_matches(text=text)

            result = ghost.transform_text(text=text, matches=matches)

            if export:  # todo: gets overwritten when using multiple files
                export_to_json(
                    object=result,
                    filename=export,
                    suffix=str(page)
                )

            doc.manipulate_page(page=page, transformer=result)

            print(f"{document} page {page}\n{result.transformed_text}")

# ---------------------------------------------------------------------------- #


@app.command()
def s3(
    log: LogLevel = LogLevel.INFO
) -> None:
    """
    Process an AWS S3 document or folder (pdf, jpg, png, or tiff).
    """
    setup_logging(level=log)
    pass  # todo


# ---------------------------------------------------------------------------- #

if __name__ == "__main__":
    command = typer.main.get_command(app)

    try:
        result = command(standalone_mode=False)
    except Exception as exception:
        raise exception

    sys.exit(0)

# ---------------------------------------------------------------------------- #
