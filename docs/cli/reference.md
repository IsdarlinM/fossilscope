# CLI Reference — fossilscope v0.2.0

Generated from the registered command surface. Every registered command below uses the same Click/Typer command tree used at runtime.

## Root help

```text
Usage: fossilscope [OPTIONS] COMMAND [ARGS]...

  Attack Surface Archaeology + Temporal Security Graph.

Options:
  --install-completion  Install completion for the current shell.
  --show-completion     Show completion for the current shell, to copy it or
                        customize the installation.
  -h, --help            Show this message and exit.

Commands:
  version
  doctor            Check runtime, SRIC integration, plugin registry and...
  init
  workspace         Manage isolated investigation workspaces.
  config            Inspect configuration and explain where a value comes...
  add
  import
  collect           Normalize an explicit passive-source export; never...
  extract           Passively extract endpoint/domain references from a...
  timeline
  diff
  fossils
  correlate
  validate
  export
  lifecycle         Show candidate fossil lifecycle without equating...
  graph-at          Render the temporal graph at a supplied point in time.
  api-diff          Compare supplied historical/current API...
  confidence        Explain confidence decay for evidence that has not...
  clusters          Group supplied observations by explicit...
  acquisitions      Show explicit acquisition/brand lineage relationships...
  report
  demo
  web
  evidence          Store a local evidence artifact in SRIC...
  ai                Show AI mode.
  plugins           List SRIC plugin manifests without auto-executing...
  scope             Evaluate a target using SRIC Scope Engine; no request...
  query             Search this workspace's shared SRIC graph.
  notebook          List/append research notes or manage saved...
  evidence-lineage  Explain evidence lineage and the reason a derived...
  jobs              List/inspect/cancel persistent SRIC jobs for this...
  update            Check/install a signed wheel release.
  help
```

## `fossilscope acquisitions`

```text
Usage: fossilscope acquisitions [OPTIONS] WORKSPACE

  Show explicit acquisition/brand lineage relationships with
  evidence/confidence.

Arguments:
  WORKSPACE  [required]

Options:
  --root PATH  [default: /home/oai/.fossilscope/workspaces]
  -h, --help   Show this message and exit.
```

## `fossilscope add`

```text
Usage: fossilscope add [OPTIONS] WORKSPACE OBSERVATION_ID ENTITY_TYPE VALUE
                       SOURCE

Arguments:
  WORKSPACE       [required]
  OBSERVATION_ID  [required]
  ENTITY_TYPE     [required]
  VALUE           [required]
  SOURCE          [required]

Options:
  --first-seen [%Y-%m-%d|%Y-%m-%dT%H:%M:%S|%Y-%m-%d %H:%M:%S]
  --last-seen [%Y-%m-%d|%Y-%m-%dT%H:%M:%S|%Y-%m-%d %H:%M:%S]
  --current-reachable / --no-current-reachable
  --auth-relevance / --no-auth-relevance
                                  [default: no-auth-relevance]
  --sensitivity-hint / --no-sensitivity-hint
                                  [default: no-sensitivity-hint]
  --current-reference / --no-current-reference
                                  [default: no-current-reference]
  --evidence TEXT
  --root PATH                     [default: /home/oai/.fossilscope/workspaces]
  -h, --help                      Show this message and exit.
```

## `fossilscope ai`

```text
Usage: fossilscope ai [OPTIONS]

  Show AI mode. Cloud AI remains disabled until explicitly configured.

Options:
  -h, --help  Show this message and exit.
```

## `fossilscope api-diff`

```text
Usage: fossilscope api-diff [OPTIONS] WORKSPACE BEFORE AFTER

  Compare supplied historical/current API specifications passively.

Arguments:
  WORKSPACE  [required]
  BEFORE     [required]
  AFTER      [required]

Options:
  --root PATH  [default: /home/oai/.fossilscope/workspaces]
  -h, --help   Show this message and exit.
```

## `fossilscope clusters`

```text
Usage: fossilscope clusters [OPTIONS] WORKSPACE

  Group supplied observations by explicit lineage/acquisition/issuer hints.

Arguments:
  WORKSPACE  [required]

Options:
  --root PATH  [default: /home/oai/.fossilscope/workspaces]
  -h, --help   Show this message and exit.
```

## `fossilscope collect`

```text
Usage: fossilscope collect [OPTIONS]

  Normalize an explicit passive-source export; never performs hidden crawling.

Options:
  --workspace TEXT
  --adapter TEXT
  --path PATH
  --root PATH       [default: /home/oai/.fossilscope/workspaces]
  -h, --help        Show this message and exit.
```

## `fossilscope confidence`

```text
Usage: fossilscope confidence [OPTIONS] WORKSPACE VALUE

  Explain confidence decay for evidence that has not been re-observed.

Arguments:
  WORKSPACE  [required]
  VALUE      [required]

Options:
  --stale-after-days INTEGER RANGE
                                  [default: 365; x>=1]
  --root PATH                     [default: /home/oai/.fossilscope/workspaces]
  -h, --help                      Show this message and exit.
```

## `fossilscope config`

```text
Usage: fossilscope config [OPTIONS] [ACTION] [KEY]

  Inspect configuration and explain where a value comes from.

Arguments:
  [ACTION]  show|explain  [default: show]
  [KEY]

Options:
  --workspace TEXT
  --root PATH       [default: /home/oai/.fossilscope/workspaces]
  -h, --help        Show this message and exit.
```

## `fossilscope correlate`

```text
Usage: fossilscope correlate [OPTIONS] WORKSPACE

Arguments:
  WORKSPACE  [required]

Options:
  --root PATH  [default: /home/oai/.fossilscope/workspaces]
  -h, --help   Show this message and exit.
```

## `fossilscope demo`

```text
Usage: fossilscope demo [OPTIONS]

Options:
  --workspace TEXT  [default: demo]
  --root PATH       [default: /home/oai/.fossilscope/workspaces]
  -h, --help        Show this message and exit.
```

## `fossilscope diff`

```text
Usage: fossilscope diff [OPTIONS] WORKSPACE
                        BEFORE:[%Y-%m-%d|%Y-%m-%dT%H:%M:%S|%Y-%m-%d %H:%M:%S]
                        AFTER:[%Y-%m-%d|%Y-%m-%dT%H:%M:%S|%Y-%m-%d %H:%M:%S]

Arguments:
  WORKSPACE                       [required]
  BEFORE:[%Y-%m-%d|%Y-%m-%dT%H:%M:%S|%Y-%m-%d %H:%M:%S]
                                  [required]
  AFTER:[%Y-%m-%d|%Y-%m-%dT%H:%M:%S|%Y-%m-%d %H:%M:%S]
                                  [required]

Options:
  --root PATH  [default: /home/oai/.fossilscope/workspaces]
  -h, --help   Show this message and exit.
```

## `fossilscope doctor`

```text
Usage: fossilscope doctor [OPTIONS]

  Check runtime, SRIC integration, plugin registry and secure defaults.

Options:
  -h, --help  Show this message and exit.
```

## `fossilscope evidence`

```text
Usage: fossilscope evidence [OPTIONS] WORKSPACE FILE

  Store a local evidence artifact in SRIC content-addressed storage.

Arguments:
  WORKSPACE  [required]
  FILE       [required]

Options:
  --source TEXT      [default: user]
  --media-type TEXT  [default: application/octet-stream]
  --redacted
  --root PATH        [default: /home/oai/.fossilscope/workspaces]
  -h, --help         Show this message and exit.
```

## `fossilscope evidence-lineage`

```text
Usage: fossilscope evidence-lineage [OPTIONS] WORKSPACE ARTIFACT_ID

  Explain evidence lineage and the reason a derived artifact is visible.

Arguments:
  WORKSPACE    [required]
  ARTIFACT_ID  [required]

Options:
  --root PATH  [default: /home/oai/.fossilscope/workspaces]
  -h, --help   Show this message and exit.
```

## `fossilscope export`

```text
Usage: fossilscope export [OPTIONS] WORKSPACE OUTPUT

Arguments:
  WORKSPACE  [required]
  OUTPUT     [required]

Options:
  --root PATH  [default: /home/oai/.fossilscope/workspaces]
  -h, --help   Show this message and exit.
```

## `fossilscope extract`

```text
Usage: fossilscope extract [OPTIONS] WORKSPACE PATH

  Passively extract endpoint/domain references from a local text artifact.

Arguments:
  WORKSPACE  [required]
  PATH       [required]

Options:
  --source TEXT  [default: local_artifact]
  --root PATH    [default: /home/oai/.fossilscope/workspaces]
  -h, --help     Show this message and exit.
```

## `fossilscope fossils`

```text
Usage: fossilscope fossils [OPTIONS] WORKSPACE

Arguments:
  WORKSPACE  [required]

Options:
  --root PATH  [default: /home/oai/.fossilscope/workspaces]
  -h, --help   Show this message and exit.
```

## `fossilscope graph-at`

```text
Usage: fossilscope graph-at [OPTIONS] WORKSPACE

  Render the temporal graph at a supplied point in time.

Arguments:
  WORKSPACE  [required]

Options:
  --at TEXT    ISO-8601 timestamp for time-travel graph.
  --root PATH  [default: /home/oai/.fossilscope/workspaces]
  -h, --help   Show this message and exit.
```

## `fossilscope help`

```text
Usage: fossilscope help [OPTIONS] [COMMAND]

Arguments:
  [COMMAND]

Options:
  -h, --help  Show this message and exit.
```

## `fossilscope import`

```text
Usage: fossilscope import [OPTIONS] WORKSPACE PATH

Arguments:
  WORKSPACE  [required]
  PATH       [required]

Options:
  --root PATH  [default: /home/oai/.fossilscope/workspaces]
  -h, --help   Show this message and exit.
```

## `fossilscope init`

```text
Usage: fossilscope init [OPTIONS] NAME

Arguments:
  NAME  [required]

Options:
  --root PATH  [default: /home/oai/.fossilscope/workspaces]
  -h, --help   Show this message and exit.
```

## `fossilscope jobs`

```text
Usage: fossilscope jobs [OPTIONS] WORKSPACE

  List/inspect/cancel persistent SRIC jobs for this workspace.

Arguments:
  WORKSPACE  [required]

Options:
  --id TEXT
  --cancel
  --root PATH  [default: /home/oai/.fossilscope/workspaces]
  -h, --help   Show this message and exit.
```

## `fossilscope lifecycle`

```text
Usage: fossilscope lifecycle [OPTIONS] WORKSPACE

  Show candidate fossil lifecycle without equating historical evidence to
  current exposure.

Arguments:
  WORKSPACE  [required]

Options:
  --root PATH  [default: /home/oai/.fossilscope/workspaces]
  -h, --help   Show this message and exit.
```

## `fossilscope notebook`

```text
Usage: fossilscope notebook [OPTIONS] WORKSPACE

  List/append research notes or manage saved investigation queries.

Arguments:
  WORKSPACE  [required]

Options:
  --type TEXT
  --title TEXT
  --body TEXT
  --status TEXT           [default: OBSERVED]
  --save-query-name TEXT
  --query TEXT
  --list-queries
  --root PATH             [default: /home/oai/.fossilscope/workspaces]
  -h, --help              Show this message and exit.
```

## `fossilscope plugins`

```text
Usage: fossilscope plugins [OPTIONS]

  List SRIC plugin manifests without auto-executing plugin code.

Options:
  --path PATH  [default: /home/oai/.sric/plugins]
  -h, --help   Show this message and exit.
```

## `fossilscope query`

```text
Usage: fossilscope query [OPTIONS] WORKSPACE QUERY

  Search this workspace's shared SRIC graph.

Arguments:
  WORKSPACE  [required]
  QUERY      [required]

Options:
  --limit INTEGER RANGE  [default: 50; 1<=x<=500]
  --root PATH            [default: /home/oai/.fossilscope/workspaces]
  -h, --help             Show this message and exit.
```

## `fossilscope report`

```text
Usage: fossilscope report [OPTIONS] WORKSPACE OUTPUT

Arguments:
  WORKSPACE  [required]
  OUTPUT     [required]

Options:
  --root PATH  [default: /home/oai/.fossilscope/workspaces]
  -h, --help   Show this message and exit.
```

## `fossilscope scope`

```text
Usage: fossilscope scope [OPTIONS] TARGET

  Evaluate a target using SRIC Scope Engine; no request is sent.

Arguments:
  TARGET  [required]

Options:
  --method TEXT  [default: GET]
  --allow TEXT
  --deny TEXT
  -h, --help     Show this message and exit.
```

## `fossilscope timeline`

```text
Usage: fossilscope timeline [OPTIONS] WORKSPACE

Arguments:
  WORKSPACE  [required]

Options:
  --root PATH  [default: /home/oai/.fossilscope/workspaces]
  -h, --help   Show this message and exit.
```

## `fossilscope update`

```text
Usage: fossilscope update [OPTIONS]

  Check/install a signed wheel release. Never performs a blind git pull.

Options:
  --check
  --manifest TEXT
  --public-key PATH
  -h, --help         Show this message and exit.
```

## `fossilscope validate`

```text
Usage: fossilscope validate [OPTIONS] WORKSPACE CANDIDATE_ID

Arguments:
  WORKSPACE     [required]
  CANDIDATE_ID  [required]

Options:
  --evidence TEXT
  --confirm / --no-confirm  [default: no-confirm]
  --root PATH               [default: /home/oai/.fossilscope/workspaces]
  -h, --help                Show this message and exit.
```

## `fossilscope version`

```text
Usage: fossilscope version [OPTIONS]

Options:
  -h, --help  Show this message and exit.
```

## `fossilscope web`

```text
Usage: fossilscope web [OPTIONS] WORKSPACE

Arguments:
  WORKSPACE  [required]

Options:
  --host TEXT     [default: 127.0.0.1]
  --port INTEGER  [default: 8767]
  --root PATH     [default: /home/oai/.fossilscope/workspaces]
  -h, --help      Show this message and exit.
```

## `fossilscope workspace`

```text
Usage: fossilscope workspace [OPTIONS] [ACTION] [NAME]

  Manage isolated investigation workspaces.

Arguments:
  [ACTION]  create|list|show|archive  [default: list]
  [NAME]

Options:
  --root PATH  [default: /home/oai/.fossilscope/workspaces]
  --confirm    Required for archive.
  -h, --help   Show this message and exit.
```
