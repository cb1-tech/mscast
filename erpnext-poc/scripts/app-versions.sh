#!/usr/bin/env bash
# Print the version of every app in an image. The build strips .git, so the
# version comes from each package's own __version__.
IMG=${1:?usage: app-versions.sh <image>}
docker run --rm --entrypoint bash "$IMG" -c 'cd /home/frappe/frappe-bench && for a in $(ls apps); do
  v=$(./env/bin/python -c "import $a; print(getattr($a, \"__version__\", \"?\"))" 2>/dev/null || echo "?")
  printf "  %-18s %s\n" "$a" "$v"; done'
