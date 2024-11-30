# pyghost

A simple library and cli tool to pseudonymize and anonymize documents. Pyghost offers

- A CLI tool and a library.
- Configurable and extendible matchers and transformers. You can write your own matchers and transformers or choose from pre-configured transformers from the pyghost library. The latter also includes Spacy-based NLP matchers.
- Importing from and exporting to AWS S3.
- Text-based anonymization and pseudonymization.
- Replacing text directly in documents using AWS Textract and Pillow.

>  **_WARNING_** This software uses various techniques to replace personal data with pseudonyms or dummy data. However, anonymization and pseudonymization are not foolproof and may not prevent re-identification of individuals. The effectiveness of the software depends on various factors, including the completeness and quality of your configuration, the quality of the source data, and the technical sophistication of potential attackers. We cannot guarantee the complete anonymity or confidentiality of your data using this software. It is your responsibility to assess the risks associated with anonymization or pseudonymization and to take appropriate measures to protect your privacy and the privacy of others.

## 1. Installation

To install pyghost, you can use pip.

```bash
pip install pyghost
```

If pyghost is not available via pip, you can also install it from a local folder, e.g.

```bash
pip install ../pyghost
```

## 2. Use Pyghost as a CLI

The pyghost CLI offers three commands:

|Command|Description|
|-|-|
|text|Process direct text input|
|local|Process local files|
|s3|Process files in an AWS S3 bucket|

You can find more information on these commands by executing

```bash
python -m pyghost --help
```

or 

```bash
python -m pyghost <command> --help
```

### 2.1 Text Input

The most simple way to use pyghost is to enter text directly.

```bash
python -m pyghost text "My name is John Doe, I am from Dublin, I work for Allianz, and my email is john.doe@example.com"
```

To show what pyghost is doing, you can print debug information.

```bash
python -m pyghost text "My name is John Doe, I am from Dublin, I work for Allianz, and my email is john.doe@example.com" --log DEBUG
```

You can also specify the location of a custom config file.

```bash
python -m pyghost text "My name is John Doe, I am from Dublin, I work for Allianz, and my email is john.doe@example.com" --config config.json
```

If you do not specify a config file, the default configuration in ``config/default.json`` will be used. To create your own configuration, just copy the default configuration and edit it using any text editor.

### 2.2 Local Documents

todo

### 2.3 AWS S3 Document

todo

## 3. Use Pyghost as a Library

todo