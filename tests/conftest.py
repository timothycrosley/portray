import contextlib
import os
import tempfile

import pytest


@contextlib.contextmanager
def chdir_manager(directory):
    old_directory = os.getcwd()
    os.chdir(directory)
    yield directory
    os.chdir(old_directory)


@pytest.fixture(scope="function")
def chdir():
    return chdir_manager


@pytest.fixture(scope="function")
def temporary_dir():
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture()
def project_dir():
    yield os.path.abspath(os.path.join(__file__, os.pardir, os.pardir))
