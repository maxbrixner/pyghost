# ---------------------------------------------------------------------------- #

import typer
import logging
import enum
import sys
import pathlib
from typing import Optional

# ---------------------------------------------------------------------------- #

from .pseudonymizer import Pseudonymizer

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


def setup_logging(level: LogLevel):
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


@app.command()
def text(
    text: str,
    log: LogLevel = LogLevel.INFO,
    config: Optional[pathlib.Path] = None
) -> None:
    """
    Process a text string.
    """
    setup_logging(level=log)

    pseudonymizer = Pseudonymizer(config=config)

    result = pseudonymizer.process(text=text)

    print(result)

# ---------------------------------------------------------------------------- #


@app.command()
def doc(
    log: LogLevel = LogLevel.INFO
) -> None:
    """
    Process a local document (pdf, jpg, png, or tiff).
    """
    setup_logging(level=log)

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
