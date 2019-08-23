import os
from pprint import pprint

import hug
import pdoc
import pdoc.cli
from mkdocs.commands.build import build as mkdocs_build

from portray import config


@hug.cli()
def html(directory: str = os.getcwd(), config_file: str = "pyproject.toml"):
    config = read_config(directory, config_file)
    pdoc.cli.main(config["pdoc3"])
    return mkdocs_build(config["mkdocs"])


@hug.cli(output=pprint)
def read_config(directory: str = os.getcwd(), config_file: str = "pyproject.toml"):
    return config.project(directory=directory, config_file=config_file)
