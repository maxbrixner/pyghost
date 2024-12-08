>  **_WARNING_** This software employs techniques to replace personal data with pseudonyms or dummy data. However, please note that anonymization and pseudonymization are not infallible and may not entirely prevent re-identification. The software's effectiveness is influenced by factors such as the completeness and quality of your configuration, the source data, and the potential attacker's technical capabilities. We cannot guarantee complete anonymity or confidentiality of your data using this software. It is your responsibility to evaluate the risks associated with anonymization or pseudonymization and implement appropriate measures to safeguard your privacy and the privacy of others.

# Pyghost

Pyghost is a simple tool for document anonymization and pseudonymization. It provides:

- **Flexible Interface**: A user-friendly command-line interface (CLI) and a versatile library for seamless integration into your projects.
- **Customizable Anonymization**: Easily configure and extend matchers and transformers to tailor your anonymization process to specific needs. Choose from built-in options, including powerful NLP-based matchers powered by Spacy.
- **Seamless Cloud Integration**: Effortlessly import and export documents from and to AWS S3 for efficient workflow management.
- **Comprehensive Text Anonymization**: Effectively anonymize and pseudonymize text-based documents.
- **Advanced Document Editing**: Directly manipulate documents using OCR providers and Pillow to precisely replace sensitive information.

## 1. Installation

Using pip:

```bash
pip install pyghost
```

Installing from a local directory:

```bash
pip install ../pyghost
```

To leverage Spacy-based NLP matchers, install the desired language models:

```bash
python -m spacy download en_core_web_sm
python -m spacy download de_core_news_sm
...
```

For local Optical Character Recognition (OCR) using Tesseract, ensure it's installed with the required language packs:

```bash
sudo apt-get install tesseract-ocr
sudo apt-get install tesseract-ocr-eng
sudo apt-get install tesseract-ocr-deu
...
```

## 2. Use pyghost as a CLI

The pyghost CLI offers three commands:

|Command|Description|
|-|-|
|text|Process text directly from the command line.|
|doc|Process local files on your system.|
|s3|Process files stored in an AWS S3 bucket.|

For more detailed information on a specific command, use:

```bash
python -m pyghost --help
```

or 

```bash
python -m pyghost <command> --help
```

### 2.1 The "text" Command

Pyghost allows you to anonymize text directly from the command line. 

Command usage:

```bash
python -m pyghost text <language> <text>
```

For example:

```bash
python -m pyghost text en "My name is John Doe, I was born in Dublin, I work for Allianz, and my email is john.doe@example.com. My wife's name is Jane Doe. Ireland is so beautiful this time of the year."
```

Output:

```
My name is <person> <person>, I was born in <location>, I work for <organization>, and my email is <email>. My wife's name is <person> <person>. <location> is so beautiful this time of the year.
```

### 2.2 The "doc" Command

Pyghost can effectively anonymize and pseudonymize various document formats, including PDF, JPG, TIFF, and PNG. Here's a breakdown of the process:

- **Optical Character Recognition (OCR)**: Pyghost extracts text from the document using OCR.
- **Text Anonymization/Pseudonymization**: The extracted text is processed to replace sensitive information with placeholders.
- **Document Modification**: Pyghost overlays the original document with boxes containing the anonymized/pseudonymized text.
- **Output**: The modified document is saved. If the source was an image file, original file format will be preserved. If the source was a PDF file, it will be converted to images.

Command usage:

```bash
python -m pyghost doc <language> <document_paths...>
```

For example:

```bash
python -m pyghost doc en test/document1EN.pdf
```

Output:

The processed document will be saved in the same directory as the input file. The output filenames will be generated based on the original filenames and page numbers. If you want to save them in another directory, you can use the ``--output`` option, e.g.,

```bash
python -m pyghost doc en test/document1EN.pdf --output test/output.jpg
```

The output filename for the exported images will be automatically generated based on the original filename and page number.

### 2.3 The "s3" Command

todo

### 2.4 Switching the OCR Provider

By default, Pyghost uses the first available OCR provider that matches the document language. However, you can explicitly choose an OCR provider using the ``--ocr`` option:

```bash
python -m pyghost text en "My name is John Doe, I was born in Dublin, I work for Allianz, and my email is john.doe@example.com. My wife's name is Jane Doe. Ireland is so beautiful this time of the year." --ocr tesseractEN
```

You can configure OCR providers in the [configuration](pyghost/config/default.json).

Pyghost offers several pre-configured options:

|Name|Description|
|-|-|
|TesseractEN|Google's Tesseract OCR for English documents. It runs locally and requires no additional setup beyond Tesseract and language pack installation (refer to the "Installation" section).
|TesseractDE|Similar to TesseractEN, but configured for German documents.
|Textract|Amazon's Textract OCR service. This option requires your AWS credentials set as environment variables. Refer to the provided [sample env-file](.env.example) file for details.|

### 2.4 Switching the Text Transformer

Pyghost allows you to control how matched text is replaced during anonymization/pseudonymization. You can achieve this by specifying a transformer using the ``--transformer`` option:

```bash
python -m pyghost text en "My name is John Doe, I was born in Dublin, I work for Allianz, and my email is john.doe@example.com. My wife's name is Jane Doe. Ireland is so beautiful this time of the year." --transformer Randomizer
```

If no transformer is specified, Pyghost will use the first transformer defined in your [Configuration](pyghost/config/default.json).

Pyghost provides pre-configured transformers for various replacement strategies:

|Name|Description|
|-|-|
|Label|Replaces each matched word with a label, like "person" for names.|
|Randomizer|Generates random letters to replace matched words while preserving case sensitivity and specific characters (spaces, punctuation).|

### 2.5 Enable Logging

For detailed insights into Pyghost's processing steps, you can activate debug logging using the ``--log`` option:

```bash
python -m pyghost text en "My name is John Doe, I was born in Dublin, I work for Allianz, and my email is john.doe@example.com. My wife's name is Jane Doe. Ireland is so beautiful this time of the year." --log DEBUG
```

### 2.6 Export Matches and Replacements

Pyghost allows you to export a JSON file containing details about all identified matches and their transformations. This can be helpful for auditing purposes or further analysis. Use the ``--export-matches`` option:

```bash
python -m pyghost text en "My name is John Doe, I was born in Dublin, I work for Allianz, and my email is john.doe@example.com. My wife's name is Jane Doe. Ireland is so beautiful this time of the year." --export-matches matches.json
```

When using the ``doc`` or ``s3`` commands, the output filename for the exported JSON will be automatically generated based on the original filename and page number.

### 2.7 Loading a Custom Configuration

Pyghost allows you to customize various settings through a configuration file. This provides flexibility to tailor the anonymization process to your specific needs.

```bash
python -m pyghost text en "My name is John Doe, I was born in Dublin, I work for Allianz, and my email is john.doe@example.com. My wife's name is Jane Doe. Ireland is so beautiful this time of the year." --config config.json
```

If no custom configuration file is specified, Pyghost will use the default settings located in [config/default.json](pyghost/config/default.json).

## 3. Use Pyghost as a Library

todo