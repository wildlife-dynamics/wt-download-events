# Migration Plan: Legacy Compiler → wt-compiler

Migrate workflow repos from `ecoscope-workflows compile` (3-package task library) to `wt-compiler compile` (unified `ecoscope-platform`).

## Prerequisites

These are already done and published — no per-repo action needed:
- `wt-compiler 0.5.0` — includes deepcopy fix for RJSF overrides (wt#128/wt#129)
- `ecoscope-workflows-ext-custom 0.1.0rc2` — entry point group changed to `wt_registry`, `pandasql` added to dependencies (ecoscope-workflow-task-library#121)

## Steps

### 1. Update spec.yaml

Replace the 3-package setup with 2 packages:

```yaml
# Before
requirements:
  - name: ecoscope-workflows-core
    version: ">=0.22.16, <0.23.0"
    channel: https://repo.prefix.dev/ecoscope-workflows/
  - name: ecoscope-workflows-ext-ecoscope
    version: ">=0.22.16, <0.23.0"
    channel: https://repo.prefix.dev/ecoscope-workflows/
  - name: ecoscope-workflows-ext-custom
    version: ">=0.0.36, <0.1.0"
    channel: https://repo.prefix.dev/ecoscope-workflows-custom/

# After
requirements:
  - name: ecoscope-platform
    version: "2.11.6"
    channel: https://repo.prefix.dev/ecoscope-workflows/
  - name: ecoscope-workflows-ext-custom
    version: "0.1.0rc2"
    channel: https://repo.prefix.dev/ecoscope-workflows-custom/
```

### 2. Replace root pixi.toml

Replace with a minimal default env containing only compile tools:

```toml
[workspace]
name = "<repo-name>"
channels = ['https://repo.prefix.dev/ecoscope-workflows/', 'conda-forge']
platforms = ['linux-64', 'osx-arm64', 'win-64']

[dependencies]
wt-compiler = "0.5.0"
graphviz = "*"
```

Key changes:
- `[project]` → `[workspace]` (pixi deprecation)
- Remove `default` env with curl/rattler-build/yq/hatch
- Remove `compile` feature/env — use `default` directly
- Remove `ecoscope-workflows-custom` channel (not needed for compiler)

### 3. Update dev/recompile.sh

```bash
# Replace this:
run_cmd ecoscope-workflows compile --spec spec.yaml --clobber ${flags}

# With this:
run_cmd wt-compiler compile \
  --spec spec.yaml \
  --pkg-name-prefix=ecoscope-workflows \
  --results-env-var=ECOSCOPE_WORKFLOWS_RESULTS \
  --clobber ${flags}
```

Also update pixi commands to remove `-e compile`:
- `pixi run --manifest-path pixi.toml -e compile` → `pixi run --manifest-path pixi.toml`
- `pixi update --manifest-path pixi.toml -e compile` → `pixi update --manifest-path pixi.toml`

### 4. Recompile

```bash
# First time (no existing lockfile for new compiler output):
bash dev/recompile.sh --install

# Subsequent (preserves lockfile, bumps version):
git checkout main -- ecoscope-workflows-*-workflow/VERSION.yaml
bash dev/recompile.sh --update
```

### 5. Test

```bash
bash dev/pytest-cli.sh <workflow-id> --all --skip-setup --quiet
```

### 6. Update CI workflows

**_recompile.yml** — already calls `bash dev/recompile.sh`, no change needed if recompile.sh is updated.

**test.yml** — remove `pixi run -e default` wrapper:
```yaml
# Before
pixi run --manifest-path pixi.toml -e default bash dev/pytest-cli.sh ...

# After
bash dev/pytest-cli.sh ...
```

**_discover.yml** — no changes needed.

### 7. Commit and version bump

```bash
git checkout main -- ecoscope-workflows-*-workflow/VERSION.yaml
bash dev/recompile.sh --update
```

This carries over the lockfile and bumps the minor version.

### 8. Create PR

```bash
gh issue create --title "feat: migrate to wt-compiler framework" \
  --body "Migrate from legacy ecoscope-workflows compiler to wt-compiler 0.5.0 with ecoscope-platform." \
  --assignee @me

git push -u origin $(git branch --show-current)

gh pr create --title "Migrate to wt-compiler framework" --body "## Summary
- Replace 3-package requirements with ecoscope-platform + ext-custom
- Switch to wt-compiler 0.5.0
- Simplify pixi.toml and CI workflows
- Recompile and bump version

Closes #<issue-number>

🤖 Generated with Claude Code"
```

### 9. Check CI status

```bash
gh pr checks <pr-number> --repo <owner>/<repo>
```

All checks should pass: discover, validate-spec, recompile-workflows, test-workflows (ubuntu, macos, windows).

### 10. Create QA issue

```bash
gh issue create --title "qa: verify <workflow-id> after wt-compiler migration" \
  --body "Manual QA for the wt-compiler migration PR #<pr-number>.

- [ ] No functional regression from pre-migration behavior"
```

## Troubleshooting

### Local channel errors during compile
```
Error: could not find subdir 'noarch' in channel 'file:///tmp/ecoscope-workflows-custom/release/artifacts/'
```
The compiler probes local file channels as fallbacks. Create stub repodata:
```bash
for dir in /tmp/ecoscope-workflows/release/artifacts /tmp/ecoscope-workflows-custom/release/artifacts; do
  mkdir -p $dir/noarch $dir/osx-arm64
  for sub in $dir/noarch $dir/osx-arm64; do
    echo '{"info":{},"packages":{},"packages.conda":{},"removed":[],"repodata_version":2}' > $sub/repodata.json
  done
done
```

### Using editable path for local task library testing
To test against local ext-custom source (e.g., before publishing):
```yaml
# In spec.yaml, replace the conda requirement:
  - name: ecoscope-workflows-ext-custom
    path: /Users/yunwu/MEP/wt-infra/ecoscope-workflow-task-library/src/ecoscope-workflows-ext-custom
    editable: true
```
The compiler installs it via pip into the ephemeral env. Remember to switch back to the published version before committing.

### Using wt_env for local compile
`wt_env` (in bash_profile) activates a pixi env with editable installs of wt-compiler and related packages from `/Users/yunwu/MEP/wt-infra/wt/`. Useful for testing compiler fixes locally:
```bash
source ~/.bash_profile && wt_env && bash dev/recompile.sh --local --install
```
The `--local` flag skips pixi and runs commands directly.

### Version conflicts
`ext-custom 0.1.0rc2` requires `ecoscope-platform >=2.11.6`. If you see a solve failure, bump ecoscope-platform version in spec.yaml.

### RJSF overrides bleeding between task instances
Fixed in wt-compiler 0.5.0. If you see one task instance's defaults/descriptions appearing on another instance of the same task, ensure you're using wt-compiler >= 0.5.0.
