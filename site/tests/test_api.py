import os
import shutil
import tempfile
import webbrowser

import hug
import mkdocs.commands.gh_deploy
import pytest

from portray import api, exceptions


def test_as_html(temporary_dir, project_dir, chdir):
    with chdir(temporary_dir):
        # Directory with no project
        with pytest.raises(exceptions.NoProjectFound):
            api.as_html()

        # Rendering should succeed as soon as a project is within the directory
        temp_project_dir = os.path.join(temporary_dir, "portray")
        shutil.copytree(project_dir, temp_project_dir)
        with chdir(temp_project_dir):
            api.as_html()

            # Rendering a second time should fail
            with pytest.raises(exceptions.DocumentationAlreadyExists):
                api.as_html()

            # Unless we enable overwritting destination
            api.as_html(overwrite=True)


def test_server(mocker, project_dir, chdir):
    with chdir(project_dir):
        mocker.patch("hug.api.HTTPInterfaceAPI.serve")
        api.server()
        hug.api.HTTPInterfaceAPI.serve.assert_called_once()


def project_configuration(project_dir, chdir):
    with chdir(project_dir):
        config = api.project_configuration()
        assert config
        assert isinstance(config, dict)


def test_in_browser(mocker, project_dir, chdir):
    with chdir(project_dir):
        mocker.patch("hug.api.HTTPInterfaceAPI.serve")
        mocker.patch("webbrowser.open_new")
        api.in_browser()
        hug.api.HTTPInterfaceAPI.serve.assert_called_once()


def test_on_github_pages(mocker, project_dir, chdir):
    with chdir(project_dir):
        mocker.patch("mkdocs.commands.gh_deploy.gh_deploy")
        api.on_github_pages()
        mkdocs.commands.gh_deploy.gh_deploy.assert_called_once()
