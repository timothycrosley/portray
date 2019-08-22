"""Defines config defaults and how config information is loaded"""
import os

import mkdocs.config as _mkdocs_config
import mkdocs.exceptions as _mkdocs_exceptions
import toml

MKDOCS_DEFAULTS = {
    "site_name": os.path.basename(os.getcwd()),
    "theme": {"name": "material", "palette": {"primary": "green", "accent": "lightgreen"}},
}


def mkdocs(**config_values) -> _mkdocs_config.base.Config:
    config = _mkdocs_config.Config(schema=_mkdocs_config.DEFAULT_SCHEMA)
    config.load_dict(MKDOCS_DEFAULTS)
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
