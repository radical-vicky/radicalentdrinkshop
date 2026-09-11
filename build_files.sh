#!/bin/bash
# Runs during every Vercel build (see vercel.json's static-build step).
set -o errexit

uv pip install -r requirements.txt

python manage.py collectstatic --noinput --clear

python manage.py migrate --noinput
