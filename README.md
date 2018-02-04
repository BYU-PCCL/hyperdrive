# hyperdrive

> Clustering tools for the BYU PCCL.

## Requirements

- [python>=3.2]
- [pip3]

## Installation

```
pip3 install git+https://github.com/BYU-PCCL/hyperdrive.git
```

## Usage

For usage instructions, consult the output of:

```
hyperdrive --help
```

## Developing

```
# optional
python3 -m venv env && source env/bin/activate
```

```
pip3 install -e .
```

To see all available commands:
```
python3 setup.py --help-commands
```

### Running unit tests

```
python3 setup.py test
```

[python>=3.2]: http://docs.python-guide.org/en/latest/starting/installation/
[pip3]: https://pip.pypa.io/en/stable/installing/
