#!/usr/bin/env bash
set -euo pipefail

script_directory="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repository_root="$(cd "${script_directory}/.." && pwd)"
image_name="$(<"${script_directory}/environment/image-tag.txt")"

if ! command -v docker >/dev/null 2>&1; then
  echo "Clean build requires Docker." >&2
  exit 2
fi

docker build \
  --file "${script_directory}/environment/Dockerfile" \
  --tag "${image_name}" \
  "${script_directory}/environment"

docker run --rm \
  --user "$(id -u):$(id -g)" \
  --env TEXMFCONFIG=/tmp/texmf-config \
  --env TEXMFHOME=/tmp/texmf-home \
  --env TEXMFVAR=/tmp/texmf-var \
  --env XDG_CACHE_HOME=/tmp/cache \
  --volume "${repository_root}:/work" \
  "${image_name}" \
  --root /work/manuscript \
  --output-dir /work/manuscript/build
