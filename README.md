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

### 2.1 Text Command

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

To enable a more verbose output, you can print debug information.

```bash
python -m pyghost text en "My name is John Doe, I was born in Dublin, I work for Allianz, and my email is john.doe@example.com. My wife's name is Jane Doe. Ireland is so beautiful this time of the year." --log DEBUG
```

You can also specify the location of a custom config file.

```bash
python -m pyghost text en "My name is John Doe, I was born in Dublin, I work for Allianz, and my email is john.doe@example.com. My wife's name is Jane Doe. Ireland is so beautiful this time of the year." --config config.json
```

If you do not specify a config file, the default configuration in ``config/default.json`` will be used. To create your own configuration, just copy the default configuration and edit it using any text editor. See the chapter on configuration for details.

It is also possible to export the mapping table as a json file. This file will contain all matches and transformations.

```bash
python -m pyghost text en "My name is John Doe, I was born in Dublin, I work for Allianz, and my email is john.doe@example.com. My wife's name is Jane Doe. Ireland is so beautiful this time of the year." --export output.json
```

### 2.2 Doc Command

```bash
python -m pyghost doc en test/document1EN.pdf
```

### 2.3 S3 Command

todo

## 3. Use pyghost as a Library

todo