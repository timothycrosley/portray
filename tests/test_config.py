import os

from hypothesis_auto import auto_test

from portray import config, exceptions

FAKE_SETUP_FILE = """
from setuptools import setup

setup(name='fake',
      version='0.1',
      description='Fake package for tesitng pourposes',
      author='Flying Circus',
      author_email='flyingcircus@example.com',
      license='MIT',
      packages=['fake'])
"""

FAKE_PYPROJECT_TOML_FLIT = """
[tool.flit.metadata]
module = "preconvert"
author = "Timothy Edmund Crosley"
author-email = "timothy.crosley@gmail.com"
home-page = "https://github.com/timothycrosley/preconvert"
requires-python=">=3.5"
description-file="README.md"
classifiers=[
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Topic :: Software Development :: Libraries :: Python Modules",
]

[tool.portray.pdoc3]
just = "kidding"
"""


def test_project_properties(project_dir):
    auto_test(config.project, _auto_allow_exceptions=(exceptions.NoProjectFound,))
    auto_test(
        config.project, directory=project_dir, _auto_allow_exceptions=(exceptions.NoProjectFound,)
    )


def test_project_setup_py(temporary_dir):
    with open(os.path.join(temporary_dir, "setup.py"), "w") as setup_file:
        setup_file.write(FAKE_SETUP_FILE)

    project_config = config.project(directory=temporary_dir, config_file="")
    assert project_config["modules"] == ["fake"]


def test_project_flit_setup(temporary_dir):
    with open(os.path.join(temporary_dir, "pyproject.toml"), "w") as setup_file:
        setup_file.write(FAKE_PYPROJECT_TOML_FLIT)

    project_config = config.project(directory=temporary_dir, config_file="pyproject.toml")
    assert project_config["modules"] == ["preconvert"]


def test_setup_py_properties():
    auto_test(config.setup_py)


def test_toml_properties():
    auto_test(config.toml)


def test_mkdocs_properties():
    auto_test(config.mkdocs)


def test_pdocs_properties():
    auto_test(config.pdocs)


def test_repository_properties():
    auto_test(config.repository)


def test_repository_custom_config(project_dir):
    assert config.repository(project_dir) == {
        "edit_uri": "edit/master/",
        "repo_name": "portray",
        "repo_url": "https://github.com/timothycrosley/portray",
    }

    assert config.repository(project_dir, repo_name="different_name") == {
        "edit_uri": "edit/master/",
        "repo_name": "different_name",
        "repo_url": "https://github.com/timothycrosley/portray",
    }

    assert config.repository(project_dir, edit_uri="edit/develop/") == {
        "edit_uri": "edit/develop/",
        "repo_name": "portray",
        "repo_url": "https://github.com/timothycrosley/portray",
    }

    assert config.repository(
        project_dir, repo_url="https://github.com/timothycrosley/examples"
    ) == {
        "edit_uri": "edit/master/",
        "repo_name": "examples",
        "repo_url": "https://github.com/timothycrosley/examples",
    }

    assert config.repository(
        project_dir, repo_url="https://bitbucket.org/atlassian/stash-example-plugin.git"
    ) == {
        "edit_uri": "src/default/docs/",
        "repo_name": "stash-example-plugin",
        "repo_url": "https://bitbucket.org/atlassian/stash-example-plugin",
    }

    assert config.repository(
        project_dir, repo_url="git@bitbucket.org:atlassian/stash-example-plugin.git"
    ) == {
        "edit_uri": "src/default/docs/",
        "repo_name": "stash-example-plugin",
        "repo_url": "https://bitbucket.org/atlassian/stash-example-plugin",
    }

    assert config.repository(project_dir, repo_url="not_actually_a_valid_url") == {
        "repo_name": "not_actually_a_valid_url",
        "repo_url": "not_actually_a_valid_url",
    }

    assert config.repository(
        project_dir, repo_url="https://gitlab.ci.token:password@gitlab.net/app.git"
    ) == {"edit_uri": "edit/master/", "repo_name": "app", "repo_url": "https://gitlab.net/app"}


def test_repository_no_config_no_repository(temporary_dir):
    assert config.repository(temporary_dir) == {}
