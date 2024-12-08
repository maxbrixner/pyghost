>  **_WARNING_** This software employs techniques to replace personal data with pseudonyms or dummy data. However, please note that anonymization and pseudonymization are not infallible and may not entirely prevent re-identification. The software's effectiveness is influenced by factors such as the completeness and quality of your configuration, the source data, and the potential attacker's technical capabilities. We cannot guarantee complete anonymity or confidentiality of your data using this software. It is your responsibility to evaluate the risks associated with anonymization or pseudonymization and implement appropriate measures to safeguard your privacy and the privacy of others.

# pyghost

A simple library and CLI to pseudonymize and anonymize documents. Pyghost offers

- A CLI tool and a library.
- Configurable and extendible matchers and transformers. You can write your own matchers and transformers or choose from pre-configured transformers from the pyghost library. The latter also includes Spacy-based NLP matchers.
- Importing from and exporting to AWS S3.
- Text-based anonymization and pseudonymization.
- Replacing text directly in documents using AWS Textract and Pillow.

## 1. Installation

To install pyghost, you can use pip.

```bash
pip install pyghost
```

If pyghost is not available via pip, you can also install it from a local folder, e.g.

```bash
pip install ../pyghost
```

If you plan to use Spacy matchers, you need to install the respective models, e.g.

```bash
python -m spacy download en_core_web_sm
python -m spacy download de_core_news_sm
...
```

If you plan to use Tesseract for local OCR, make sure it is installed, e.g.

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
|text|Process direct text input|
|doc|Process local files|
|s3|Process files in an AWS S3 bucket|

You can find more information on these commands by executing

```bash
python -m pyghost --help
```

or 

```bash
python -m pyghost <command> --help
```

### 2.1 The "text" Command

The most simple way to use pyghost is to enter text directly.

```bash
python -m pyghost text <language> <text>
```

For example

```bash
python -m pyghost text en "My name is John Doe, I was born in Dublin, I work for Allianz, and my email is john.doe@example.com. My wife's name is Jane Doe. Ireland is so beautiful this time of the year."
```

The output should look somewhat like this:

```
My name is <person> <person>, I was born in <location>, I work for <organization>, and my email is <email>. My wife's name is <person> <person>. <location> is so beautiful this time of the year.
```

### 2.2 The "doc" Command

You can use pyghost to pseudonymize and anonymize documents. This works wor PDF, JPG, TIFF, and PNG files. In order to achieve this, pyghost will

- Run optical character recognition (OCR) on the file.
- Pseudonymize/Anonymize the document's text.
- Output the transformed text.
- Output the original document but with pseudonymized/anonymized content.

To pseudonymize/anonymize the original document, pyghost will draw a solid box over the original text and attempt to print the new text inside this box. It will automatically try to set the font size, so that the new text fits into this box.

```bash
python -m pyghost doc <language> <documents...>
```

For example

```bash
python -m pyghost doc en test/document1EN.pdf
```

The resulting files will be saved in the same folder as the source files. If you want to save them in another directory, you can use the ``--ouput`` option, e.g.

```bash
python -m pyghost doc en test/document1EN.pdf --output test/output.jpg
```

The output filename will automatically be manipulated so that it contains the original filename and page number.

### 2.3 The "s3" Command

todo

### 2.4 Switching the OCR Provider

If you want to switch to another OCR provider, you can use the ``--ocr`` option, e.g.

```bash
python -m pyghost text en "My name is John Doe, I was born in Dublin, I work for Allianz, and my email is john.doe@example.com. My wife's name is Jane Doe. Ireland is so beautiful this time of the year." --ocr tesseractEN
```

If the ``--ocr`` is not set, the first OCR provider that matches the given language is used. You can configure OCR providers in the [Configuration](pyghost/config/default.json).

The following OCR providers are preconfigured:

|Name|Description|
|-|-|
|TesseractEN|Google's Tesseract OCR (configured for English documents) runs locally and does not require any credentials. Please make sure that tesseract and the language packs are installed (see "Installation").
|TesseractDE|Google's Tesseract OCR (configured for German documents) runs locally and does not require any credentials. Please make sure that tesseract and the language packs are installed (see "Installation").
|Textract|Amazon's Textract OCR. This requires your AWS credentials as environment variables. See [the sample env-File](.env.example) for details.|

### 2.4 Switching the Text Transformer

The text transformer controls how your matches are replaced in the text or documents. If you want to change how text is replaced, you can use the ``--transformer`` option, e.g.

```bash
python -m pyghost text en "My name is John Doe, I was born in Dublin, I work for Allianz, and my email is john.doe@example.com. My wife's name is Jane Doe. Ireland is so beautiful this time of the year." --transformer Randomizer
```

 If the ``--transformer`` is not set, the first transformer in your configuration is used. You can configure transformers in the [Configuration](pyghost/config/default.json).

The following transformers are preconfigured:

|Name|Description|
|-|-|
|Label|Replaces each word with its label, e.g. "John" by "<person>".
|Randomizer|Replaces each word with random letters. The Randomizer is case sensitive and preserves certain letters like spaces or punctuation.|

### 2.5 Enable Logging

To enable a more verbose output, you can print debug information using the ``--log`` option.

```bash
python -m pyghost text en "My name is John Doe, I was born in Dublin, I work for Allianz, and my email is john.doe@example.com. My wife's name is Jane Doe. Ireland is so beautiful this time of the year." --log DEBUG
```

### 2.6 Export Matches and Replacements

It is possible to export the mapping table as a json file using the ``--export-matches`` option. This file will contain all matches and transformations.

```bash
python -m pyghost text en "My name is John Doe, I was born in Dublin, I work for Allianz, and my email is john.doe@example.com. My wife's name is Jane Doe. Ireland is so beautiful this time of the year." --export-matches matches.json
```

If you use the ``doc`` or ``s3`` command, the filename will automatically be manipulated so that it contains the original filename and page number.

### 2.7 Loading a Custom Configuration

You can also specify the location of a custom config file.

```bash
python -m pyghost text en "My name is John Doe, I was born in Dublin, I work for Allianz, and my email is john.doe@example.com. My wife's name is Jane Doe. Ireland is so beautiful this time of the year." --config config.json
```

If you do not specify a config file, the default configuration in ``config/default.json`` will be used. To create your own configuration, just copy the default configuration and edit it using any text editor. See the chapter on configuration for details.



## 3. Use pyghost as a Library

todo