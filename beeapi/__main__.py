import json
import logging

import click
import pandas as pd

from beeapi.utility import Utility
from tqdm import tqdm


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@click.group()
def ciit():
    pass


@ciit.command()
@click.option("--config", type=click.File("rb"))
@click.option("--csv", type=click.File("rb"))
def load_measures_from_csv(config, csv):
    """
    Import measures from CSV to BeeData API
    \f
    :param file config: utility configuration file
    :param file csv: measures CSV file
    """

    utility = Utility(json.load(config))
    measures = pd.read_csv(
        csv,
        sep=";",
        encoding="utf-8",
        names=["id", "ts", "value", "period", "unit", "type"],
    )

    groups = measures.groupby(["id", "type", "period", "unit"])
    with tqdm(total=groups.ngroups) as pbar:
        for name, group in groups:
            id, measures_type, period, unit = name
            utility.post_measures(group, id, measures_type, period, unit)
            pbar.update()


if __name__ == "__main__":
    ciit(obj={})
