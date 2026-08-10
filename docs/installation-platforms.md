# Installation and uninstallation

| Platform | Install | Uninstall |
|---|---|---|
| Linux / Termux | `sh scripts/install-linux.sh` | `sh scripts/uninstall-linux.sh` |
| Windows | `scripts\install-windows.cmd` | `scripts\uninstall-windows.cmd` |

The Windows uninstaller removes the `fossilscope.cmd` shim and isolated FossilScope venv while preserving workspaces, configuration, cache and evidence. The shared `%USERPROFILE%\.local\bin` PATH entry is intentionally retained for sibling Sentinel Forge tools. Linux follows the same data-preservation policy.
