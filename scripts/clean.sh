#!/bin/bash
set -euxo pipefail

poetry run ruff . --fix
poetry run black portray/ tests/
