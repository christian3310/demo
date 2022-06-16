# Stock Parser

Parse listed stocks and the daily top3 of each industry.

## Before start

This project use poetry to manage packages and environment, please install it if you don't have poetry on your computer.

```
pip install -U poetry
```

then run this command to do initialization.

```
poetry install
```

To activate virtualenv, exec the following command:

```
poetry shell
```

## Usage

```
python -m app -h
```

```
usage: __main__.py [-h] [-v] [-d DATE]

Parse and save listed stocks information and the daily top3 stocks of each industry.

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         increase output verbosity
  -d DATE, --date DATE  parse specific date, the valid format is yyyy-mm-dd, set as today if not specify
```

To parse the information of today, run the following command:

```
python -m app
```

To parse the information of specific date, like 2022/05/17, please run as the following:

```
python -m app -d 2022-05-17
```

The result would be saved to the `data` folder.

## Runtime

If the virtualenv has benn activated, run the command directly. otherwise you should run with `poetry run`.

```
poetry run python -m app
```

## Test

Just execute `pytest` to run the testing.