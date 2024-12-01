from setuptools import setup, find_packages

package_name = "pyghost"
version = "0.1.0"
description = "A simple library and cli tool to pseudonymize and anonymize documents"
author = "Max Brixner"
author_email = "max.brixner@allianz.de"

dependencies = [
    "typer",
    "spacy",
    "pydantic",
    "pdf2image",
    "pillow",
    "pytesseract"
]

setup(
    name=package_name,
    version=version,
    description=description,
    author=author,
    author_email=author_email,
    packages=find_packages(),
    install_requires=dependencies if dependencies else [],
)
