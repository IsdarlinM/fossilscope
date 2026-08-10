# Updates

The official FossilScope update channel is zero-config:

```bash
fossilscope update --check
fossilscope update
fossilscope update --force
```

Normal users do **not** provide a manifest or public key. SRIC resolves the fixed official `IsdarlinM/fossilscope` channel, requires an immutable GitHub signature-verified release commit, validates the downloaded source ZIP and its `pyproject.toml`, backs up state, installs without a shell, and verifies the installed distribution version.

`fossilscope update --check` verifies official release metadata without installing. `fossilscope update` installs a newer official release. `fossilscope update --force` reinstalls the official release even when that exact version is already installed and uses pip `--force-reinstall` for that explicit force operation.

`--force` never permits a downgrade. `--check` and `--force` are mutually exclusive. Normal upgrades require rollback metadata matching the currently installed version; same-version force reinstalls use the verified target snapshot as the recovery package.

## Windows post-exit update

Windows cannot safely replace the active `fossilscope.exe` in place. The official updater therefore verifies and stages the release while the visible FossilScope process is still running, then performs installation only after that process exits.

For FossilScope 0.5.16 and later, the visible process also builds and verifies the target and rollback wheels **before** handoff. The post-exit helper accepts only prebuilt `.whl` artifacts; it never starts a source-build backend after detaching. Helper subprocesses use `CREATE_NO_WINDOW`, so a normal `fossilscope update` or same-version `fossilscope update --force` must not open additional command-prompt/CLI windows.

A same-version forced reinstall reports the operation explicitly:

```text
"same_version": true
"forced": true
"action": "FORCED_REINSTALL"
"staged": true
```

`update_available` may remain `false` in this case because there is no newer release; the requested action is nevertheless a deliberate verified reinstall. The final post-exit result is written under `~/.fossilscope/update-result.json` and detailed subprocess output is retained in `~/.fossilscope/update-handoff.log`. Runtime mutation happens only after staging succeeds.

If staging/build verification fails, the current runtime is left untouched and no post-exit handoff is started. If post-exit installation fails, the verified rollback wheel is attempted before the update lock is cleared.

## Advanced custom channel

`--manifest` and `--public-key` remain available together for private/custom channels. The corresponding `FOSSILSCOPE_RELEASE_MANIFEST_URL` and `FOSSILSCOPE_RELEASE_PUBLIC_KEY` environment variables are treated as an explicit custom-channel override. Supplying only one side is rejected.

Custom channels retain Ed25519 manifest verification and SHA-256 wheel verification. HTTP update sources and blind `git pull` remain prohibited.
