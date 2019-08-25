#!/bin/bash -xe

poetry run isort --recursive portray/ tests/
poetry run black portray/ tests/ -l 100
