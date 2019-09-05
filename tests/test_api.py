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

            # Or, we output to a different location
            with tempfile.TemporaryDirectory() as new_temp_directory:
                api.as_html(output_dir=os.path.join(new_temp_directory, "site"))


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


def test_module_no_path(temporary_dir, chdir):
    """Test handling of python modules specified in root project directory but not in path"""
    with chdir(temporary_dir):
        with open(os.path.join(temporary_dir, "my_module.py"), "w") as pathless_module:
            pathless_module.write("def my_method():\n    pass\n")

        # Rendering with no module identification should fail
        with pytest.raises(Exception):
            api.as_html()

        # With module specification, even without path should succeed
        api.as_html(modules=["my_module"])

        # Unless path auto inclusion is turned off
        with open(os.path.join(temporary_dir, "pyproject.toml"), "w") as pyproject:
            pyproject.write("[tool.portray]\nappend_directory_to_python_path = false")
        with pytest.raises(Exception):
            api.as_html()
