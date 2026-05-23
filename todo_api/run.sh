#!/bin/bash
# Run the Todo API with Clean Architecture
cd "$(dirname "$0")"
export PYTHONPATH="$(pwd)/app:$PYTHONPATH"
source venv/bin/activate
exec uvicorn main:app --host 0.0.0.0 --port 8000 "$@"
