#!/usr/bin/env sh
set -eu
INSTALL_ROOT="${HOME}/.fossilscope"
BIN="${HOME}/.local/bin/fossilscope"
rm -f "$BIN"
rm -rf "$INSTALL_ROOT"
echo "Removed FossilScope. User-created workspaces outside $INSTALL_ROOT were not touched."
