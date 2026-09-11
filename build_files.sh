#!/bin/bash
set -o errexit

# Ensure uv resolves against 3.12 regardless of what the static-build
# step auto-detected. Vercel's @vercel/static-build doesn't read the
# runtime field from vercel.json — only @vercel/python does.
export UV_PYTHON=3.12

uv pip install --system -r requirements.txt

python manage.py collectstatic --noinput --clear

python manage.py migrate --noinput
