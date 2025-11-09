#!/bin/bash
# Script para ejecutar tests con el venv correcto

cd "$(dirname "$0")"
source ../.venv/bin/activate
# Desactivar plugin de langsmith que causa problemas con Python 3.12
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest test_ai_generation.py -p no:langsmith "$@"
