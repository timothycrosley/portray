#!/bin/bash
set -euxo pipefail

poetry run isort portray/ tests/
poetry run black portray/ tests/
