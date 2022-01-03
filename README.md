# beeapi

[![CI](https://github.com/beedata-analytics/beeapi/actions/workflows/main.yml/badge.svg)](https://github.com/beedata-analytics/beeapi/actions/workflows/main.yml)
[![Dependencies Status](https://img.shields.io/badge/dependencies-up%20to%20date-brightgreen.svg)](https://github.com/beedata-analytics/beeapi/pulls?utf8=%E2%9C%93&q=is%3Apr%20author%3Aapp%2Fdependabot)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/beedata-analytics/beeapi/blob/master/.pre-commit-config.yaml)

Beedata Analytics API client

## Installation

```bash
pip install git+https://github.com/beedata-analytics/beeapi.git
```

## Command line client

    $ beeapi --help

### load-measures-from-csv

    $ beeapi load-measures-from-csv --help

    $ beeapi load-measures-from-csv --config=config.json --csv=quartihoraries.csv


## Library usage

```python
from beeapi import Client


client = Client(
    {
        "beedata": {
            "company_id": 1234567890,
            "auth": {
                "username": "username",
                "password": "password",
                "cert_file": "cert/1234567890.crt",
                "key_file": "cert/1234567890.key",
            },
            "endpoints": {
                "contracts": "v1/contracts",
                "measures": "v1/amon_measures",
            },
            "base_url": "https://api.beedataanalytics.com/",
            "timezone": "Europe/Madrid",
        }
    }
)
```
