"""Defines config defaults and how config information is loaded"""
import os

import mkdocs.config as _mkdocs_config
import mkdocs.exceptions as _mkdocs_exceptions
from toml import load as toml_load
from git import Repo
from urllib import parse

MKDOCS_DEFAULTS = {
    "site_name": os.path.basename(os.getcwd()),
    "theme": {"name": "material", "palette": {"primary": "green", "accent": "lightgreen"}},
    "markdown_extensions": ["admonition", "codehilite", "extra"]
}


def repository(directory: str) -> dict:
    config = {}
    try:
        config['repo_url'] = Repo(directory).remotes.origin.url
        config['repo_name'] = parse.urlsplit(config["repo_url"]).path.rstrip('.git').lstrip('/')
    except Exception:
        print("WARNING: Unable to identify `repo_name` and `repo_url` automatically")

    return config


def mkdocs(directory: str, **config_values) -> _mkdocs_config.base.Config:
    config = _mkdocs_config.Config(schema=_mkdocs_config.DEFAULT_SCHEMA)
    config.load_dict(MKDOCS_DEFAULTS)
    config.load_dict(repository(directory))
    config.load_dict(config_values)

    errors, warnings = config.validate()
    if errors:
        raise _mkdocs_exceptions.ConfigurationError(
            "Aborted with {} Configuration Errors!".format(len(errors))
        )
    elif config["strict"] and warnings:
        raise _mkdocs_exceptions.ConfigurationError(
            "Aborted with {} Configuration Warnings in 'strict' mode!".format(len(warnings))
        )

    return config


def toml(location: str, **overrides) -> dict:
    config = toml_load(location).get("tool", {}).get("portray", {})
    config.update(overrides)
    config['file'] = location
    return config


def project(directory: str, config_file: str, **overrides) -> dict:
    project_config = toml(os.path.join(directory, config_file))
    project_config['mkdocs'] = mkdocs(directory, **project_config.get('mkdocs', {}))
    return project_config
