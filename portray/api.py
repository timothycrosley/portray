import os
import shutil
import glob

import pdoc
import pdoc.cli
import tempfile
from mkdocs.commands.build import build as mkdocs_build

from portray import config


def html(directory: str = os.getcwd(), config_file: str = "pyproject.toml", output_dir: str="site"):
    with tempfile.TemporaryDirectory() as input_dir:
        input_dir = os.path.join(input_dir, "input")
        with tempfile.TemporaryDirectory() as temp_output_dir:
            shutil.copytree(directory, input_dir)

            nav = []
            markdown_documents = glob.glob(os.path.join(input_dir, "**/*.md"), recursive=True)
            if "README.md" in markdown_documents:
                markdown_documents.remove("README.md")
                nav.append({"Home": "README.md"})
            for document in markdown_documents:
                nav.append({os.path.basename(document)[:-3].replace("-", " ").replace("_", " ").capitalize(): document})

            config = read_config(directory, config_file, context={"input_dir": input_dir, 'output_dir': temp_output_dir, 'nav': nav})
            pdoc.cli.main(config["pdoc3"])
            mkdocs_build(config["mkdocs"])
            shutil.copytree(temp_output_dir, output_dir)


def read_config(directory: str = os.getcwd(), config_file: str = "pyproject.toml", context=None):
    return config.project(directory=directory, config_file=config_file, context=context)
