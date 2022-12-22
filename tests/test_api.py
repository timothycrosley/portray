import os
import shutil
import sys
import tempfile

import mkdocs.commands.gh_deploy
import pytest
import toml
from portray import api, exceptions

CUSTOM_NAV = """
[[tool.portray.mkdocs.nav]]
Changelog = "CHANGELOG.md"

[[tool.portray.mkdocs.nav]]
Troubleshooting = "TROUBLESHOOTING.md"

[[tool.portray.mkdocs.nav]]
    [[tool.portray.mkdocs.nav.Contributing]]
    "1. Contributing Guide" = "docs/contributing/1.-contributing-guide.md"

    [[tool.portray.mkdocs.nav.Contributing]]
    "2. Coding Standard" = "docs/contributing/2.-coding-standard.md"

    [[tool.portray.mkdocs.nav.Contributing]]
    "3. Code of Conduct" = "docs/contributing/3.-code-of-conduct.md"

    [[tool.portray.mkdocs.nav.Contributing]]
    "4. Acknowledgements" = "docs/contributing/4.-acknowledgements.md"

[[tool.portray.mkdocs.nav]]
    [[tool.portray.mkdocs.nav."Quick Start"]]
    "1. Installation" = "docs/quick_start/1.-installation.md"

    [[tool.portray.mkdocs.nav."Quick Start"]]
    "2. CLI" = "docs/quick_start/2.-cli.md"

    [[tool.portray.mkdocs.nav."Quick Start"]]
    "3. API" = "docs/quick_start/3.-api.md"

    [[tool.portray.mkdocs.nav."Quick Start"]]
    "4. Configuration" = "docs/quick_start/4.-configuration.md"
"""

FAKE_PYPROJECT_TOML_BASIC = """
[tool.portray]
modules = ["my_module"]
output_dir = "docs_output"
"""


@pytest.mark.skipif(
    sys.version_info < (3, 8) and sys.platform == "win32",
    reason="Tests fails on CI with this combination due to CI specific permission issues on.",
)
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


@pytest.mark.skipif(
    sys.version_info < (3, 8) and sys.platform == "win32",
    reason="Tests fails on CI with this combination due to CI specific permission issues on.",
)
def test_as_html_custom_nav(temporary_dir, project_dir, chdir):
    with chdir(temporary_dir):
        temp_project_dir = os.path.join(temporary_dir, "portray")
        shutil.copytree(project_dir, temp_project_dir)
        with chdir(temp_project_dir):
            with open(os.path.join(temp_project_dir, "pyproject.toml"), "w+") as pyproject:
                pyproject.write(CUSTOM_NAV)

            api.as_html()


def test_server(mocker, project_dir, chdir):
    with chdir(project_dir):
        mocker.patch("portray.api.Server")
        api.server()
        api.Server.assert_called_once()
        api.Server.return_value.serve.assert_called_once()


def test_reloading_server(mocker, project_dir, chdir):
    with chdir(project_dir):
        mocker.patch("portray.api.Server")
        api.server(reload=True)
        server_instance = api.Server.return_value
        server_instance.serve.assert_called_once()
        assert len(server_instance.watch.call_args_list) == 5

        server_instance.reset_mock()
        with tempfile.TemporaryDirectory(dir=project_dir) as test_dir:
            test_config = os.path.join(test_dir, "test.toml")
            test_docs_dir = os.path.join(test_dir, "docs_dir")
            test_site_dir = os.path.join(test_dir, "site_dir")
            os.mkdir(test_docs_dir)
            os.mkdir(test_site_dir)
            with open(test_config, "w") as test_cfg:
                toml.dump(
                    {
                        "tool": {
                            "portray": {
                                "mkdocs": {"docs_dir": test_docs_dir, "site_dir": test_site_dir}
                            }
                        }
                    },
                    test_cfg,
                )
            api.server(config_file=test_config, reload=True)
            server_instance.watch.assert_called()
            assert len(server_instance.watch.call_args_list) == 7


def project_configuration(project_dir, chdir):
    with chdir(project_dir):
        config = api.project_configuration()
        assert config
        assert isinstance(config, dict)


def test_in_browser(mocker, project_dir, chdir):
    with chdir(project_dir):
        mocker.patch("portray.api.Server")
        mocker.patch("webbrowser.open_new")
        api.in_browser()
        server_instance = api.Server.return_value
        server_instance.serve.assert_called_once()

        server_instance.reset_mock()
        api.in_browser(port=9999, host="localhost")
        call_args = server_instance.serve.call_args_list[0][1]
        assert call_args["host"] == "localhost"
        assert call_args["port"] == 9999


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


def test_setting_output_dir_in_pyproject_overwrites_default(temporary_dir):
    config_file = os.path.join(temporary_dir, "pyproject.toml")
    with open(config_file, "w") as pyproject:
        pyproject.write(FAKE_PYPROJECT_TOML_BASIC)
    config = api.project_configuration(directory=temporary_dir, config_file=config_file)
    assert config["output_dir"] == "docs_output"
