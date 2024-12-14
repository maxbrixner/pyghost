import setuptools

package_name = "pyghost"
version = "0.1.0"
description = "A simple library and CLI tool to pseudonymize and anonymize documents"
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

data_files = [("pyghost",  ["pyghost/config/default.json",
                            "pyghost/data/fake-email-en.txt",
                            "pyghost/data/fake-location-en.txt",
                            "pyghost/data/fake-name-en.txt",
                            "pyghost/data/fake-organization-en.txt",
                            "pyghost/fonts/Roboto-Regular.ttf"])]

setuptools.setup(
    name=package_name,
    version=version,
    description=description,
    author=author,
    author_email=author_email,
    packages=setuptools.find_packages(),
    install_requires=dependencies if dependencies else [],
    include_package_data=True,
    data_files=data_files
)
