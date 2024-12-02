# ---------------------------------------------------------------------------- #

import typer
import logging
import enum
import sys
import pathlib
import json
import pydantic
from typing import Any, Optional

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
        with configfile.open("r") as file:
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
    Save all matches to a json file.
    """
    if suffix:
        filename = filename.with_stem(f"{filename.stem}{suffix}")
    with filename.open("w") as file:
        content = object.model_dump()
        json.dump(content, file, indent=4)

# ---------------------------------------------------------------------------- #


@app.command()
def text(
    text: str,
    log: LogLevel = LogLevel.INFO,
    config: Optional[pathlib.Path] = None,
    export: Optional[pathlib.Path] = None
) -> None:
    """
    Process a text string.
    """
    setup_logging(level=log)
    config = load_config(configfile=config)

    ghost = Ghost(config=config)

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
    document: pathlib.Path,
    log: LogLevel = LogLevel.INFO,
    config: Optional[pathlib.Path] = None,
    export: Optional[pathlib.Path] = None
) -> None:
    """
    Process a local document (pdf, jpg, png, or tiff).
    """
    setup_logging(level=log)
    config = load_config(configfile=config)

    ghost = Ghost(config=config)
    document = Document(filename=document, config=config)

    for page, text in enumerate(document.get_text()):
        matches = ghost.find_matches(text=text)

        result = ghost.transform_text(text=text, matches=matches)

        if export:
            export_to_json(
                object=result,
                filename=export,
                suffix=str(page)
            )

        print(result.transformed_text)

# ---------------------------------------------------------------------------- #


@app.command()
def s3(
    log: LogLevel = LogLevel.INFO
) -> None:
    """
    Process an AWS S3 document or folder (pdf, jpg, png, or tiff).
    """
    setup_logging(level=log)


# ---------------------------------------------------------------------------- #

if __name__ == "__main__":
    command = typer.main.get_command(app)

    try:
        result = command(standalone_mode=False)
    except Exception as exception:
        raise exception

    sys.exit(0)

# ---------------------------------------------------------------------------- #
