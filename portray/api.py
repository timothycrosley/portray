import os
import webbrowser

import hug

from portray import config, render


def html(
    directory: str = os.getcwd(), config_file: str = "pyproject.toml", output_dir: str = "site"
):
    render.documentation(read_config(directory, config_file))


def read_config(directory: str = os.getcwd(), config_file: str = "pyproject.toml"):
    return config.project(directory=directory, config_file=config_file)


def server(
    directory: str = os.getcwd(), config_file: str = "pyproject.toml", open_browser: bool = False
):
    api = hug.API("Doc Server")

    project_config = read_config(directory, config_file)
    with render.documentation_in_temp_folder(project_config) as doc_folder:

        @hug.static("/", api=api)
        def my_static_dirs():
            return (doc_folder,)

        if open_browser:

            @hug.startup(api=api)
            def open_browser_to_docs(*args, **kwargs):
                webbrowser.open_new("{}:{}".format(project_config["host"], project_config["port"]))

        api.http.serve(
            host=project_config["host"],
            port=project_config["port"],
            no_documentation=True,
            display_intro=False,
        )


def in_browser(
    directory: str = os.getcwd(), config_file: str = "pyproject.toml", output_dir: str = "site"
):
    return server(directory=directory, config_file=config_file, open_browser=True)
