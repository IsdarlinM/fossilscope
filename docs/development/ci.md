# Local release validation

FossilScope does not depend on GitHub Actions or another hosted CI service.

```bash
python -m pip install -e ../sric-core
python -m pip install -e '.[dev]'
python scripts/release-gate.py
```

The full local gate runs compilation, Ruff, strict mypy, all pytest suites, project security/evaluation scripts when present, dependency audit, SBOM generation when available, package build, isolated wheel installation and root CLI help checks. It writes machine-readable evidence and artifact SHA-256 hashes to `build/release-evidence/`.

The `--quick` mode is for development only. A release requires a complete `PASS` report for the exact source commit.
