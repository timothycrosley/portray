#!/bin/bash -xe

./scripts/lint.sh
poetry run pytest -s --cov=portray --cov=tests --cov-report=term-missing ${@}
