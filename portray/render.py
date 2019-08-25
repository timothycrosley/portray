import os
import shutil
import tempfile
from argparse import Namespace
from contextlib import contextmanager
from glob import glob

import mkdocs.config as mkdocs_config
import mkdocs.exceptions as _mkdocs_exceptions
import pdoc.cli
from mkdocs.commands.build import build as mkdocs_build


def pdoc3(config):
    pdoc.cli.main(Namespace(**config))


def mkdocs(config):
    config_instance = mkdocs_config.Config(schema=mkdocs_config.DEFAULT_SCHEMA)
    config_instance.load_dict(config)

    errors, warnings = config_instance.validate()
    if errors:
        raise _mkdocs_exceptions.ConfigurationError(
            "Aborted with {} Configuration Errors!".format(len(errors))
        )
    elif config.get("strict", False) and warnings:
        raise _mkdocs_exceptions.ConfigurationError(
            "Aborted with {} Configuration Warnings in 'strict' mode!".format(len(warnings))
        )

    return mkdocs_build(config_instance)


def documentation(config):
    with documentation_in_temp_folder(config) as documentation_output:
        shutil.copytree(temp_output_dir, config["output_dir"])


@contextmanager
def documentation_in_temp_folder(config):
    with tempfile.TemporaryDirectory() as input_dir:
        input_dir = os.path.join(input_dir, "input")
        with tempfile.TemporaryDirectory() as temp_output_dir:
            shutil.copytree(config["directory"], input_dir)

            if not "output_dir" in config["pdoc3"]:
                config["pdoc3"]["output_dir"] = os.path.join(input_dir, "reference")
            pdoc3(config["pdoc3"])

            if not "docs_dir" in config["mkdocs"]:
                config["mkdocs"]["docs_dir"] = input_dir
            if not "site_dir" in config["mkdocs"]:
                config["mkdocs"]["site_dir"] = temp_output_dir
            if not "nav" in config["mkdocs"]:
                nav = config["mkdocs"]["nav"] = []

                root_docs = glob(os.path.join(input_dir, "*.md"))
                readme_doc = os.path.join(input_dir, "README.md")
                if readme_doc in root_docs:
                    root_docs.remove(readme_doc)
                    nav.append({"Home": "README.md"})
                nav.extend(_doc(doc, input_dir) for doc in root_docs)

                docs_dir_docs = glob(os.path.join(input_dir, config["docs_dir"], "*.md"))
                nav.extend(_nested_docs(os.path.join(input_dir, config["docs_dir"]), input_dir))

                reference_docs = glob(os.path.join(config["pdoc3"]["output_dir"], "**/*.md"))
                nav.append({"Reference": _nested_docs(config["pdoc3"]["output_dir"], input_dir)})

            mkdocs(config["mkdocs"])
            yield temp_output_dir


def _nested_docs(directory, root_directory, include_docs=True) -> list:
    nav = [_doc(doc, root_directory) for doc in glob(os.path.join(directory, "*.md"))]

    nested_dirs = glob(os.path.join(directory, "*/"))
    for nested_dir in nested_dirs:
        nav.append({_label(nested_dir[:-1]): _nested_docs(nested_dir, root_directory)})

    return nav


def _label(path):
    return os.path.basename(path).split(".")[0].replace("-", " ").replace("_", " ").title()


def _doc(path, root_path):
    path = os.path.relpath(path, root_path)
    return {_label(path): path}
