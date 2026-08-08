#!/usr/bin/env sh
set -eu
INSTALL_ROOT="${HOME}/.fossilscope"
BIN="${HOME}/.local/bin/fossilscope"
rm -f "$BIN"
rm -rf "$INSTALL_ROOT/venv"
echo "Removed FossilScope runtime. Workspaces, configuration and evidence under $INSTALL_ROOT were preserved."
