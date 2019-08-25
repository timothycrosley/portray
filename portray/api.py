"""This module defines the programmatic API that can be used to interact with `portray`
   to generate and view documentation.

   If you want to extend `portray` or use it directly from within Python - this is the place
   to start.
"""
import os
import webbrowser

import hug

from portray import config, render


def as_html(
    directory: str = os.getcwd(), config_file: str = "pyproject.toml", output_dir: str = "site"
):
    """Produces HTML documentation for a Python project.

       - *directory*: The root folder of your project.
       - *config_file*: The [TOML](https://github.com/toml-lang/toml#toml)  formatted config file you wish to use.
       - *output_dir*: The directory to place the generated HTML into.
    """
    render.documentation(project_configuration(directory, config_file))


def in_browser(
    directory: str = os.getcwd(),
    config_file: str = "pyproject.toml",
    port: int = None,
    host: str = None,
):
    """Runs a development webserver enabling you to browse documentation locally
       then opens a web browser pointing to it.

       - *directory*: The root folder of your project.
       - *config_file*: The [TOML](https://github.com/toml-lang/toml#toml) formatted config file you wish to use.
       - *port*: The port to expose your documentation on (defaults to: `8000`)
       - *host*: The host to expose your documentation on (defaults to `"127.0.0.1"`)
    """
    return server(directory=directory, config_file=config_file, open_browser=True)


def server(
    directory: str = os.getcwd(),
    config_file: str = "pyproject.toml",
    open_browser: bool = False,
    port: int = None,
    host: str = None,
):
    """Runs a development webserver enabling you to browse documentation locally.

       - *directory*: The root folder of your project.
       - *config_file*: The [TOML](https://github.com/toml-lang/toml#toml) formatted config file you wish to use.
       - *open_browser": If true a browser will be opened pointing at the documentation server
       - *port*: The port to expose your documentation on (defaults to: `8000`)
       - *host*: The host to expose your documentation on (defaults to `"127.0.0.1"`)
    """
    api = hug.API("Doc Server")

    project_config = project_configuration(directory, config_file)
    with render.documentation_in_temp_folder(project_config) as doc_folder:

        @hug.static("/", api=api)
        def my_static_dirs():
            return (doc_folder,)

        if open_browser:

            @hug.startup(api=api)
            def open_browser_to_docs(*args, **kwargs):
                webbrowser.open_new("{}:{}".format(project_config["host"], project_config["port"]))

        api.http.serve(
            host=host or project_config["host"],
            port=port or project_config["port"],
            no_documentation=True,
            display_intro=False,
        )


def project_configuration(directory: str = os.getcwd(), config_file: str = "pyproject.toml"):
    """Returns the configuration associated with a project.

        - *directory*: The root folder of your project.
        - *config_file*: The [TOML](https://github.com/toml-lang/toml#toml) formatted config file you wish to use.
    """
    return config.project(directory=directory, config_file=config_file)
