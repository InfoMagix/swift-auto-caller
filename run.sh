#!/usr/bin/env bash
set -e
source '.venv/bin/activate'
python -u swift_auto_caller_web.py "$@"
