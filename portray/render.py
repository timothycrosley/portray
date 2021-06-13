"""Defines how to render the current project and project_config using the
included documentation generation utilities.
"""
import os
import shutil
import sys
import tempfile
from contextlib import contextmanager
from glob import glob
from typing import Dict, Iterator, Tuple

import mkdocs.config as mkdocs_config
import mkdocs.exceptions as _mkdocs_exceptions
from mkdocs.commands.build import build as mkdocs_build
from mkdocs.config.defaults import get_schema as mkdocs_schema
from mkdocs.utils import is_markdown_file
from pdocs import as_markdown as pdocs_as_markdown
from yaspin import yaspin

from portray.exceptions import DocumentationAlreadyExists

NO_HOME_PAGE = """
# Nothing here

`portray` uses README.md as your projects home page.
It appears you do not yet have a README.md file created.
"""


def documentation(config: dict, overwrite: bool = False) -> None:
    """Renders the entire project given the project config into the config's
    specified output directory.

    Behind the scenes:

    - A temporary directory is created and your code is copy and pasted there
    - pdoc is ran over your code with the output sent into the temporary directory
        as Markdown documents
    - MkDocs is ran over all of your projects Markdown documents including those
        generated py pdoc. MkDocs outputs an HTML representation to a new temporary
        directory.
    - The html temporary directory is copied into your specified output location
    - Both temporary directories are deleted.
    """
    if os.path.exists(config["output_dir"]):
        if overwrite:
            shutil.rmtree(config["output_dir"])
        else:
            raise DocumentationAlreadyExists(config["output_dir"])

    with documentation_in_temp_folder(config) as (_, documentation_output):
        shutil.copytree(documentation_output, config["output_dir"])


def pdocs(config: dict) -> None:
    """Render this project using the specified pdoc config passed into pdoc.

    This rendering is from code definition to Markdown so that
    it will be compatible with MkDocs.
    """
    pdocs_as_markdown(**config)


def mkdocs(config: dict):
    """Render the project's associated Markdown documentation using the specified
    MkDocs config passed into the MkDocs `build` command.

    This rendering is from `.md` Markdown documents into HTML
    """
    config_instance = _mkdocs_config(config)
    return mkdocs_build(config_instance)


@contextmanager
def documentation_in_temp_folder(config: dict) -> Iterator[Tuple[str, str]]:
    """Build documentation within a temp folder, returning that folder name before it is deleted."""
    if config["append_directory_to_python_path"] and not config["directory"] in sys.path:
        sys.path.append(config["directory"])

    with tempfile.TemporaryDirectory() as input_dir:
        input_dir = os.path.join(input_dir, "input")
        os.mkdir(input_dir)
        with tempfile.TemporaryDirectory() as temp_output_dir:

            with yaspin(
                text="Copying source documentation to temporary compilation directory"
            ) as spinner:
                for root_file in os.listdir(config["directory"]):
                    root_file_absolute = os.path.join(config["directory"], root_file)
                    if os.path.isfile(root_file_absolute) and is_markdown_file(root_file_absolute):
                        shutil.copyfile(root_file_absolute, os.path.join(input_dir, root_file))

                for source_directory in [config["docs_dir"]] + config["extra_dirs"]:
                    directory_absolute = os.path.join(config["directory"], source_directory)
                    if os.path.isdir(directory_absolute):
                        shutil.copytree(
                            directory_absolute, os.path.join(input_dir, source_directory)
                        )

                spinner.ok("Done")

            if "docs_dir" not in config["mkdocs"]:
                config["mkdocs"]["docs_dir"] = input_dir
            if "site_dir" not in config["mkdocs"]:
                config["mkdocs"]["site_dir"] = temp_output_dir
            if "nav" not in config["mkdocs"]:
                nav = config["mkdocs"]["nav"] = []

                root_docs = sorted(glob(os.path.join(input_dir, "*.md")))
                readme_doc = os.path.join(input_dir, "README.md")
                if readme_doc in root_docs:
                    root_docs.remove(readme_doc)
                else:
                    with open(readme_doc, "w") as readme_doc_file:
                        readme_doc_file.write(NO_HOME_PAGE)

                nav.append({"Home": "README.md"})

                nav.extend(_doc(doc, input_dir, config) for doc in root_docs)

                nav.extend(
                    _nested_docs(os.path.join(input_dir, config["docs_dir"]), input_dir, config)
                )
            else:
                nav = config["mkdocs"]["nav"]
                if nav:
                    index_nav = nav[0]
                    index_page: str = ""
                    if index_nav and isinstance(index_nav, dict):
                        index_page = tuple(index_nav.values())[0]
                    elif isinstance(index_nav, str):  # pragma: no cover
                        index_page = index_nav

                    if index_page:

                        destination_index_page = os.path.join(input_dir, "index.md")
                        if (
                            index_page != "README.md"
                            and index_page != "index.md"
                            and not os.path.exists(destination_index_page)
                        ):
                            shutil.copyfile(
                                os.path.join(input_dir, index_page), destination_index_page
                            )

            if config["include_reference_documentation"]:
                with yaspin(text="Auto generating reference documentation using pdocs") as spinner:
                    if "output_dir" not in config["pdocs"]:
                        config["pdocs"]["output_dir"] = os.path.join(input_dir, "reference")
                    pdocs(config["pdocs"])
                    reference_docs = _nested_docs(config["pdocs"]["output_dir"], input_dir, config)
                    nav.append({"Reference": reference_docs})  # type: ignore
                    spinner.ok("Done")

            with yaspin(text="Rendering complete website from Markdown using MkDocs") as spinner:
                mkdocs(config["mkdocs"])
                spinner.ok("Done")

            # remove any settings pointing to the temp dirs
            if config["mkdocs"]["docs_dir"].startswith(input_dir):
                del config["mkdocs"]["docs_dir"]
            if config["mkdocs"]["site_dir"].startswith(temp_output_dir):
                del config["mkdocs"]["site_dir"]
            if config["pdocs"]["output_dir"].startswith(input_dir):
                del config["pdocs"]["output_dir"]
            if config["include_reference_documentation"]:
                nav.pop()

            yield input_dir, temp_output_dir


def _mkdocs_config(config: dict) -> mkdocs_config.Config:
    config_instance = mkdocs_config.Config(schema=mkdocs_schema())
    config_instance.load_dict(config)

    errors, warnings = config_instance.validate()
    if errors:
        print(errors)
        raise _mkdocs_exceptions.ConfigurationError(
            f"Aborted with {len(errors)} Configuration Errors!"
        )
    elif config.get("strict", False) and warnings:  # pragma: no cover
        print(warnings)
        raise _mkdocs_exceptions.ConfigurationError(
            f"Aborted with {len(warnings)} Configuration Warnings in 'strict' mode!"
        )

    config_instance.config_file_path = config["config_file_path"]
    return config_instance


def _nested_docs(directory: str, root_directory: str, config: dict) -> list:
    nav = [
        _doc(doc, root_directory, config) for doc in sorted(glob(os.path.join(directory, "*.md")))
    ]

    nested_dirs = sorted(glob(os.path.join(directory, "*/")))
    for nested_dir in nested_dirs:
        if (
            len(glob(os.path.join(nested_dir, "*.md")) + glob(os.path.join(nested_dir, "**/*.md")))
            > 0
        ):
            dir_nav = {
                _label(nested_dir[:-1], config): _nested_docs(nested_dir, root_directory, config)
            }
            nav.append(dir_nav)  # type: ignore

    return nav


def _label(path: str, config: Dict) -> str:
    label = os.path.basename(path)
    if "." in label:
        label = ".".join(label.split(".")[:-1])
    label = label.replace("-", " ").replace("_", " ").title()
    return config["labels"].get(label, label)


def _doc(path: str, root_path: str, config: dict) -> Dict[str, str]:
    path = os.path.relpath(path, root_path)
    return {_label(path, config): path}
