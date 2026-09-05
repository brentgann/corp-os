#!/usr/bin/env bash
# Package the plugin as an installable .plugin bundle, after validating it.
set -euo pipefail
cd "$(dirname "$0")"
ROOT="$PWD"

python3 scripts/validate.py

mkdir -p dist
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# Build the archive outside the target tree, then move it into place. Some
# mounted filesystems refuse in-place zip replacement.
( cd plugins/corp-os && zip -rq "$TMP/corp-os.plugin" . -x "*.DS_Store" )

# Copy by truncating in place rather than mv/unlink: some synced or mounted
# filesystems permit writes but refuse deletes.
cat "$TMP/corp-os.plugin" > "$ROOT/dist/corp-os.plugin"

echo "built dist/corp-os.plugin ($(du -h "$ROOT/dist/corp-os.plugin" | cut -f1))"
