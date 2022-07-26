#!/bin/bash
set -euxo pipefail

poetry run cruft check
poetry run mypy --ignore-missing-imports portray/
poetry run isort --check --diff portray/ tests/
poetry run black --check portray/ tests/
poetry run flake8 portray/ tests/
poetry run safety check -i 39462 -i 40291 -i 49337 -i 47794
poetry run bandit -r portray/
