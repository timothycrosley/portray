import os

import hug

from portray import config, render


def html(
    directory: str = os.getcwd(), config_file: str = "pyproject.toml", output_dir: str = "site"
):
    render.documentation(read_config(directory, config_file))


def read_config(directory: str = os.getcwd(), config_file: str = "pyproject.toml"):
    return config.project(directory=directory, config_file=config_file)


def server(
    directory: str = os.getcwd(), config_file: str = "pyproject.toml", output_dir: str = "site"
):
    api = hug.API("Doc Server")

    project_config = read_config(directory, config_file)
    with render.documentation_in_temp_folder(project_config) as doc_folder:

        @hug.static("/", api=api)
        def my_static_dirs():
            return (doc_folder,)

        api.http.serve(
            host=project_config["host"],
            port=project_config["port"],
            no_documentation=True,
            display_intro=False,
        )
