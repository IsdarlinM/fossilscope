# Updates

The official FossilScope update channel is zero-config:

```bash
fossilscope update --check
fossilscope update
fossilscope update --force
```

Normal users do **not** provide a manifest or public key. SRIC resolves the fixed official `IsdarlinM/fossilscope` channel, requires an immutable GitHub signature-verified release commit, validates the downloaded source ZIP and its `pyproject.toml`, backs up state, installs without a shell, and verifies the installed distribution version.

`fossilscope update --check` verifies official release metadata without installing. `fossilscope update` installs a newer official release. `fossilscope update --force` reinstalls the **current official-channel release** even when that exact version is already installed and uses pip `--force-reinstall` for that explicit force operation. `--force` does not select an unreleased branch.

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

### Pre-release Windows handoff smoke

When the stable update channel is intentionally held behind a candidate, do **not** move the channel merely to test same-version handoff behavior. After installing/repairing the candidate into the isolated FossilScope runtime, run from the candidate checkout:

```cmd
scripts\test-windows-update-handoff.cmd
```

This developer-only smoke uses the current local checkout as the package source and substitutes only channel/download discovery. It performs no network request and does not change the production update channel. The real Windows staging code still builds a wheel, launches the post-exit helper and force-reinstalls that wheel into the isolated FossilScope venv.

Expected evidence:

```text
Windows handoff smoke PASS: one visible CLI, hidden helper result INSTALLED, forced action preserved, no stale lock.
```

During the smoke, **no additional console window should appear**. The result must contain `status=INSTALLED`, `installed=true`, `forced=true`, `action=FORCED_REINSTALL`, and the temporary update lock must be removed. This smoke validates process/handoff behavior only; it does not replace signature/channel trust tests or the complete release gate.

## Advanced custom channel

`--manifest` and `--public-key` remain available together for private/custom channels. The corresponding `FOSSILSCOPE_RELEASE_MANIFEST_URL` and `FOSSILSCOPE_RELEASE_PUBLIC_KEY` environment variables are treated as an explicit custom-channel override. Supplying only one side is rejected.

Custom channels retain Ed25519 manifest verification and SHA-256 wheel verification. HTTP update sources and blind `git pull` remain prohibited.
