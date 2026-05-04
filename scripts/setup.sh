#!/usr/bin/env bash
set -e

python -m venv .venv
source .venv/bin/activate

pip install -q -e ".[dev]"
pre-commit install

make test && echo "✅ Setup completo. Tests pasando con coverage ≥80%." || echo "❌ Falló. Revisa los errores anteriores."
