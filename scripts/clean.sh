#!/bin/bash -xe

poetry run isort --profile hug portray/ tests/
poetry run black portray/ tests/ -l 100
