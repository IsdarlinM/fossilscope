# Installation

Use `scripts/install-linux.sh` or `scripts/install-windows.cmd`. FossilScope installs into an isolated runtime and keeps workspaces, configuration, evidence and reports outside the runtime environment.

## Windows repair

If the isolated Windows runtime is incomplete or corrupted, clone/download the current FossilScope source and run:

```cmd
scripts\repair-windows.cmd
```

The repair entrypoint rebuilds only `%USERPROFILE%\.fossilscope\venv`. The existing runtime is first moved to `venv.rollback`; if installation or validation fails, the previous runtime is restored when possible. `%USERPROFILE%\.fossilscope\workspaces` and other user state are not deleted.

The Windows installer validates `annotated_types`, Pydantic, FossilScope, SRIC Web modules, `pip check`, `version`, `doctor --json`, `capabilities`, and the root help forms before reporting success.

Verify a repaired installation with:

```cmd
fossilscope version
fossilscope doctor --json
fossilscope capabilities
```
