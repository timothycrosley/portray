"""Defines config defaults and how config information is loaded"""
import os
from argparse import Namespace
from typing import Dict, List, Union, cast
from urllib import parse

import mkdocs.config as _mkdocs_config
import mkdocs.exceptions as _mkdocs_exceptions
from git import Repo
from toml import load as toml_load

MKDOCS_DEFAULTS = {
    "site_name": os.path.basename(os.getcwd()),
    "theme": {"name": "material", "palette": {"primary": "green", "accent": "lightgreen"}},
    "markdown_extensions": ["admonition", "codehilite", "extra"]
}

PDOC3_DEFAULTS = {
    "modules": [os.path.basename(os.getcwd())],
    "filter": None,
    "force": True,
    "html": False,
    "pdf": False,
    "html_dir": None,
    "html_no_source": False,
    "overwrite": False,
    "external_links": False,
    "template_dir": os.path.join(os.path.dirname(__file__), "pdoc3_templates"),
    "link_prefix": None,
    "close_stdin": False,
    "http": "",
    "config": {"show_type_annotations": True},
}  # type: Dict[str, Union[str, str, bool, None, Dict, List]]


def repository(directory: str) -> dict:
    config = {}
    try:
        config["repo_url"] = Repo(directory).remotes.origin.url
        config["repo_name"] = parse.urlsplit(config["repo_url"]).path.rstrip(".git").lstrip("/")
    except Exception:
        print("WARNING: Unable to identify `repo_name` and `repo_url` automatically")

    return config


def mkdocs(directory: str, **overrides) -> _mkdocs_config.base.Config:
    config = _mkdocs_config.Config(schema=_mkdocs_config.DEFAULT_SCHEMA)
    config.load_dict(MKDOCS_DEFAULTS)
    config.load_dict(repository(directory))
    config.load_dict(overrides)

    errors, warnings = config.validate()
    if errors:
        print(errors)
        raise _mkdocs_exceptions.ConfigurationError(
            "Aborted with {} Configuration Errors!".format(len(errors))
        )
    elif config["strict"] and warnings:
        raise _mkdocs_exceptions.ConfigurationError(
            "Aborted with {} Configuration Warnings in 'strict' mode!".format(len(warnings))
        )

    return config


def pdoc3(**overrides) -> Namespace:
    defaults = {**PDOC3_DEFAULTS}
    defaults["config"] = [
        "{}={}".format(key, value) for key, value in PDOC3_DEFAULTS["config"].items()
    ]
    defaults.update(overrides)
    return Namespace(**defaults)


def toml(location: str, **overrides) -> dict:
    config = toml_load(location).get("tool", {}).get("portray", {})
    config.update(overrides)
    config["file"] = location
    return config


def project(directory: str, config_file: str, context: Union[dict, None]=None, **overrides) -> dict:
    project_config = context.copy() if context else {}
    project_config.update(toml(os.path.join(directory, config_file), **overrides))
    if "input_dir" in context:
        if not project_config.setdefault("pdoc3", {}).get("output_dir"):
            project_config["pdoc3"]["output_dir"] = os.path.join(context["input_dir"], "reference")
        if not project_config.setdefault("mkdocs", {}).get("docs_dir"):
            project_config["mkdocs"]["docs_dir"] = context["input_dir"]

    if "output_dir" in context and not project_config["mkdocs"].get("site_dir"):
        project_config["mkdocs"]["site_dir"] = context["output_dir"]
    if "nav" in context and not project_config["mkdocs"].get("nav"):
        project_config["mkdocs"]["nav"] = context["nav"]

    project_config["mkdocs"] = mkdocs(directory, **project_config.get("mkdocs", {}))
    project_config["pdoc3"] = pdoc3(**project_config.get("pdoc3", {}))
    return project_config
