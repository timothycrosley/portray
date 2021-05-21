"""Defines the configuration defaults and load functions used by `portray`"""
import ast
import os
import re
import warnings
from pathlib import Path
from typing import Any, Dict, Optional

import _ast
import mkdocs.config as _mkdocs_config  # noqa
import mkdocs.exceptions as _mkdocs_exceptions  # noqa
from git import Repo
from toml import load as toml_load

from portray.exceptions import NoProjectFound

PORTRAY_DEFAULTS = {
    "docs_dir": "docs",
    "extra_dirs": ["art", "images", "media"],
    "output_dir": "site",
    "port": 8000,
    "host": "127.0.0.1",
    "append_directory_to_python_path": True,
    "include_reference_documentation": True,
    "labels": {"Cli": "CLI", "Api": "API", "Http": "HTTP", "Pypi": "PyPI"},
    "extra_markdown_extensions": [],
}

MKDOCS_DEFAULTS: Dict[str, Any] = {
    "site_name": os.path.basename(os.getcwd()),
    "config_file_path": os.getcwd(),
    "theme": {
        "name": "material",
        "palette": {"primary": "green", "accent": "lightgreen"},
        "custom_dir": os.path.join(os.path.dirname(__file__), "mkdocs_templates"),
    },
    "markdown_extensions": [
        "admonition",
        "codehilite",
        "extra",
        "pymdownx.details",
        "pymdownx.highlight",
    ],
}

PDOCS_DEFAULTS: Dict = {"overwrite": True, "exclude_source": False}


def project(directory: str, config_file: str, **overrides) -> dict:
    """Returns back the complete configuration - including all sub configuration components
       defined below that `portray` was able to determine for the project
    """
    if not (
        os.path.isfile(os.path.join(directory, config_file))
        or os.path.isfile(os.path.join(directory, "setup.py"))
        or "modules" in overrides
    ):
        raise NoProjectFound(directory)

    project_config: Dict[str, Any] = {**PORTRAY_DEFAULTS, "directory": directory}
    if os.path.isfile(os.path.join(directory, "setup.py")):
        project_config.update(setup_py(os.path.join(directory, "setup.py")))

    project_config.update(toml(os.path.join(directory, config_file)))
    project_config.update(overrides)

    project_config.setdefault("modules", [os.path.basename(os.getcwd()).replace("-", "_")])
    project_config.setdefault("pdocs", {}).setdefault("modules", project_config["modules"])

    mkdocs_config = project_config.get("mkdocs", {})
    mkdocs_config.setdefault(
        "extra_markdown_extensions", project_config.get("extra_markdown_extensions", [])
    )
    project_config["mkdocs"] = mkdocs(directory, **mkdocs_config)
    if "pdoc3" in project_config:
        warnings.warn(
            "pdoc3 config usage is deprecated in favor of pdocs. "
            "pdoc3 section will be ignored. ",
            DeprecationWarning,
        )
    project_config["pdocs"] = pdocs(directory, **project_config.get("pdocs", {}))
    return project_config


def setup_py(location: str) -> dict:
    """Returns back any configuration info we are able to determine from a setup.py file"""
    setup_config = {}
    try:
        with open(location) as setup_py_file:
            for node in ast.walk(ast.parse(setup_py_file.read())):
                if (
                    type(node) == _ast.Call
                    and type(getattr(node, "func", None)) == _ast.Name
                    and node.func.id == "setup"  # type: ignore
                ):
                    for keyword in node.keywords:  # type: ignore
                        if keyword.arg == "packages":
                            setup_config["modules"] = ast.literal_eval(keyword.value)
                            break
                    break
    except Exception as error:
        warnings.warn(f"Error ({error}) occurred trying to parse setup.py file: {location}")

    return setup_config


def toml(location: str) -> dict:
    """Returns back the configuration found within the projects
       [TOML](https://github.com/toml-lang/toml#toml) config (if there is one).

       Generally this is a `pyproject.toml` file at the root of the project
       with a `[tool.portray]` section defined.
    """
    try:
        location_exists = os.path.exists(location)
        if not location_exists:
            warnings.warn(f'\nNo config file found at location: "{location}"')
            return {}
    except Exception as detection_error:  # pragma: no cover
        warnings.warn(f'\nUnable to check config at "{location}" due to error: {detection_error}')

    try:
        toml_config = toml_load(location)
        tools = toml_config.get("tool", {})

        config = tools.get("portray", {})
        config["file"] = location

        if "modules" not in config:
            if "poetry" in tools and "name" in tools["poetry"]:
                config["modules"] = [tools["poetry"]["name"]]
            elif (
                "flit" in tools
                and "metadata" in tools["flit"]
                and "module" in tools["flit"]["metadata"]
            ):
                config["modules"] = [tools["flit"]["metadata"]["module"]]

        return config
    except Exception as load_config_error:
        warnings.warn(f'\nConfig file at "{location}" has errors: {load_config_error}')

    return {}


def repository(
    directory: str,
    repo_url: Optional[str] = None,
    repo_name: Optional[str] = None,
    edit_uri: Optional[str] = None,
    normalize_repo_url: bool = True,
    **kwargs,
) -> Dict[str, Optional[str]]:
    """Returns back any information that can be determined by introspecting the projects git repo
       (if there is one).
    """
    try:
        if repo_url is None:
            repo_url = Repo(directory).remotes.origin.url
        if repo_name is None:
            match = re.search(r"(:(//)?)([\w\.@\:/\-~]+)(\.git)?(/)?", repo_url)
            if match:
                path = match.groups()[2]
            else:
                path = repo_url
            repo_name = path.split("/")[-1]
            if repo_name.endswith(".git"):
                repo_name = repo_name[: -len(".git")]
        if edit_uri is None:
            if "github" in repo_url or "gitlab" in repo_url:
                edit_uri = "edit/main/"
            elif "bitbucket" in repo_url:
                edit_uri = "src/default/docs/"

        if normalize_repo_url:
            if repo_url.startswith("git@") and ":" in repo_url:
                tld, path = repo_url[4:].split(":")
                repo_url = f"https://{tld}/{path}"
            elif repo_url.startswith("https://") and "@" in repo_url:
                repo_url = f"https://{repo_url.split('@')[1]}"

            if repo_url and "github" in repo_url or "gitlab" in repo_url or "bitbucket" in repo_url:
                repo_url = repo_url.replace(".git", "")

        return {
            key: value
            for key, value in {
                "repo_url": repo_url,
                "repo_name": repo_name,
                "edit_uri": edit_uri,
            }.items()
            if value
        }

    except Exception:
        warnings.warn("Unable to identify `repo_name`, `repo_url`, and `edit_uri` automatically.")
        return {}


def mkdocs(directory: str, **overrides) -> dict:
    """Returns back the configuration that will be used when running mkdocs"""
    mkdocs_config: Dict[str, Any] = {
        **MKDOCS_DEFAULTS,
        **repository(directory, **overrides),
        **overrides,
    }
    theme = mkdocs_config["theme"]
    if theme["name"].lower() == "material":
        if "custom_dir" in theme:
            theme["custom_dir"] = Path(theme["custom_dir"]).absolute().as_posix()
        else:
            theme["custom_dir"] = MKDOCS_DEFAULTS["theme"]["custom_dir"]

    nav = mkdocs_config.get("nav", None)
    if nav and hasattr(nav[0], "copy"):
        mkdocs_config["nav"] = [nav_item.copy() for nav_item in nav]

    mkdocs_config["markdown_extensions"] = mkdocs_config["markdown_extensions"] + mkdocs_config.pop(
        "extra_markdown_extensions", []
    )

    return mkdocs_config


def pdocs(directory: str, **overrides) -> dict:
    """Returns back the configuration that will be used when running pdocs"""
    defaults = {**PDOCS_DEFAULTS}
    defaults.update(overrides)
    return defaults
