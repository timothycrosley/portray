import os
from pprint import pprint

import hug
from portray import config



@hug.cli()
def html(directory: str=os.getcwd(), config_file: str="pyproject.toml"):
    return


@hug.cli(output=pprint)
def read_config(directory: str=os.getcwd(), config_file: str="pyproject.toml"):
    return config.project(directory=directory, config_file=config_file)
