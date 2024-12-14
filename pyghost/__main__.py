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
from .text import Text
from .document import Document
from .models import Config, GhostResult

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
    Set up the logger for pyghost.
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
    try:
        if not configfile:
            configfile = pathlib.Path(__file__).parent / \
                pathlib.Path("./config/default.json")

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
) -> None:
    """
    Save a pydantic model to a json file.
    """
    with filename.open("w", encoding="utf-8") as file:
        content = object.model_dump()
        json.dump(content, file, indent=4)

# ---------------------------------------------------------------------------- #


@app.command()
def text(
    language: str,
    text: str,
    transformer: Optional[str] = None,
    log: LogLevel = LogLevel.INFO,
    config: Optional[pathlib.Path] = None,
    export_matches: Optional[pathlib.Path] = None,
) -> None:
    """
    Pseudonymize or anonymize a text.
    """
    setup_logging(level=log)
    configuration = load_config(configfile=config)

    words = Text().get_words(text=text)

    ghost = Ghost(
        language=language,
        config=configuration,
        transformer=transformer
    )

    transformation = ghost.process_text(
        text=text, words=words)

    if export_matches:
        export_to_json(
            object=GhostResult(
                matches=matches,
                transformation=transformation
            ),
            filename=export_matches
        )

    print(transformation.transformed_text)

# ---------------------------------------------------------------------------- #


@app.command()
def doc(
    language: str,
    documents: List[pathlib.Path],
    output: Optional[pathlib.Path] = None,
    ocr: Optional[str] = None,
    transformer: Optional[str] = None,
    log: LogLevel = LogLevel.INFO,
    config: Optional[pathlib.Path] = None,
    export_matches: Optional[pathlib.Path] = None
) -> None:
    """
    Pseudonymize or anonymize local documents (pdf, jpg, png, or tiff).
    """
    setup_logging(level=log)
    configuration = load_config(configfile=config)

    ghost = Ghost(
        language=language,
        config=configuration,
        transformer=transformer
    )

    document = Document(
        language=language,
        config=configuration,
        ocr_provider=ocr
    )

    for filename in documents:
        document.load(filename=filename)

        for page, doc_ocr in enumerate(document.ocr):
            transformation = ghost.process_text(
                text=doc_ocr.text, words=doc_ocr.words)

            if export_matches:
                export_to_json(
                    object=GhostResult(
                        matches=matches,
                        transformation=transformation
                    ),
                    filename=export_matches.with_stem(
                        f"{export_matches.stem}_{filename.stem}_{page}"),
                )

            document.manipulate_page(page=page, transformer=transformation)

        if output is None:
            document.save(
                filename=filename.with_stem(
                    f"out_{filename.stem}").with_suffix(".jpg")
            )
        else:
            document.save(
                filename=output.with_stem(
                    f"{output.stem}_{filename.stem}")
            )

# ---------------------------------------------------------------------------- #


@app.command()
def s3(
    log: LogLevel = LogLevel.INFO
) -> None:
    """
    Process an AWS S3 document or folder (pdf, jpg, png, or tiff).
    """
    setup_logging(level=log)
    configuration = load_config(configfile=config)

    pass  # todo


# ---------------------------------------------------------------------------- #

if __name__ == "__main__":
    """
    Run typer commands.
    """
    command = typer.main.get_command(app)

    try:
        result = command(standalone_mode=False)
    except Exception as exception:
        raise exception

    sys.exit(0)

# ---------------------------------------------------------------------------- #
