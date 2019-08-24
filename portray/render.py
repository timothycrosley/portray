import os
import tempfile
from argparse import Namespace
import shutil
from glob import glob

import pdoc.cli
import mkdocs.config as mkdocs_config
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


def _label(path):
    return os.path.basename(path)[:-3].replace("-", " ").replace("_", " ").title()


def _doc(path, root_path):
    path = os.path.relpath(path, root_path)
    return {_label(path): path}


def documentation(config):
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
                nav = []

                root_docs = glob(os.path.join(input_dir, "*.md"))
                if "README.md" in root_docs:
                    root_docs.remove("README.md")
                    nav.append({"Home": "README.md"})
                nav.extend(_doc(doc, input_dir) for doc in root_docs)

                docs_dir_docs = glob(os.path.join(input_dir, config["docs_dir"], "*.md"))
                nav.extend(_doc(doc, input_dir) for document in docs_dir_docs)

                nested_dirs = glob(os.path.join(input_dir, config["docs_dir"], "*/"))
                for nested_dir in nested_dirs:
                    nested_docs = glob(os.path.join(nested_dir, "*.md"))
                    nav.append({_label(nested_dir): [_doc(doc, input_dir) for doc in nested_docs]})

                reference_docs = glob(os.path.join(config["pdoc3"]["output_dir"], "**/*.md"))
                nav.append({"Reference": [_doc(doc, input_dir) for doc in reference_docs]})

            mkdocs(config["mkdocs"])
            shutil.copytree(temp_output_dir, config["output_dir"])
