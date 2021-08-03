#!/bin/sh

cpu_count=$(grep -c processor /proc/cpuinfo)
# https://docs.gunicorn.org/en/latest/design.html#how-many-workers
exec gunicorn -b :"${PORT:-8000}" -w $(((cpu_count * 2) + 1)) --reload wsgi:application