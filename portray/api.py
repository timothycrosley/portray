import os

from portray import config, render


def html(directory: str = os.getcwd(), config_file: str = "pyproject.toml", output_dir: str="site"):
    render.documentation(read_config(directory, config_file))


def read_config(directory: str = os.getcwd(), config_file: str = "pyproject.toml"):
    return config.project(directory=directory, config_file=config_file)
