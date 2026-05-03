# Contributing

## Branches

- **`main`** — release branch. Updated only via promotion PRs from `staging` or `patch-*`. Each merge cuts a tag + GitHub release ([`tag.yml`](.github/workflows/tag.yml)).
- **`staging`** — QA integration branch. Feature PRs land here for testing before promotion.
- **`patch-*`** — hotfix branches that bypass staging for urgent fixes that can't wait for the staging cycle.
- **Feature branches** — your working branches, conventionally named `<initials>/<topic>`. Branch off `staging`.

## QA flow

```
feature/* ──PR──▶ staging ──promotion PR──▶ main ──▶ release tag
```

1. Branch off `staging`:
   ```bash
   git checkout staging && git pull
   git checkout -b <initials>/<topic>
   ```
2. Make changes. Bump `VERSION.yaml` if `staging` isn't already ahead of `main` (see **Versioning**).
3. Open a PR targeting `staging`. CI ([`test.yml`](.github/workflows/test.yml)) must pass.
4. After merge, manually QA the workflow on `staging` as needed.
5. When ready to release, an admin runs the **Promote staging to main** workflow:
   *Actions → Promote staging to main → Run workflow.*
   It opens (or updates) a `staging → main` PR with all included commits and PRs listed.
6. Merging the promotion PR cuts a release tag + GitHub release automatically.

## Versioning

`VERSION.yaml` must be strictly greater than the version on `main` for any PR — feature → staging or staging → main. Multiple feature PRs in a single staging cycle share **one** version bump: only the first PR after a release needs to bump. Subsequent PRs inherit the already-bumped version.

## Hotfixes

For urgent fixes that can't wait for the staging cycle:

1. Branch off `main` with a name starting with `patch-`:
   ```bash
   git checkout main && git pull
   git checkout -b patch-<topic>
   ```
2. Open a PR directly to `main`. The `Guard main PRs` workflow allows `patch-*` sources to bypass staging.
3. Bump the patch version in `VERSION.yaml`.
4. After merge, port the fix back to `staging` so it isn't lost in the next release.

## Branch protection setup

One-off, run by a repo admin:

```bash
./.github/scripts/setup-branch-protection.sh
```

Configures rulesets that require PR + green CI to land on `main` and `staging`. Source-branch enforcement for `main` is handled by [`guard-main-prs.yml`](.github/workflows/guard-main-prs.yml).
