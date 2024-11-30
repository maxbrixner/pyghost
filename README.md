# pyghost

## 1. Installation

todo

## 2. Use pyghost as a CLI tool

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

### 2.1 Text input

The most simple way to use pyghost is to enter text directly.

```bash
python -m pyghost text "My email is john.doe@example.com"
```

To show what pyghost is doing, you can show debug information.

```bash
python -m pyghost text "My email is john.doe@example.com" --log DEBUG
```
