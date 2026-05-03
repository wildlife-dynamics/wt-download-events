#!/usr/bin/env bash
# Configure branch protection rulesets for the QA staging flow.
#
# Creates two rulesets on the current repo:
#   - qa-protect-main:    requires PR + green CI to land on `main`
#   - qa-protect-staging: requires PR + green CI to land on `staging`
#
# Source-branch enforcement for `main` (only `staging` or `patch-*` allowed)
# is handled by the `guard-main-prs.yml` workflow, which fails on disallowed
# sources. Add `Guard main PRs / check-source` to MAIN_REQUIRED_CHECKS below
# (after the workflow has run at least once so GitHub knows the check name).
#
# Requires:
#   - gh CLI authenticated as a user with admin access to the repo
#   - jq
#
# Usage:
#   ./.github/scripts/setup-branch-protection.sh
#
# Override defaults via env vars:
#   REPO=owner/name MAIN_REQUIRED_CHECKS="check1,check2" ./setup-branch-protection.sh

set -euo pipefail

REPO="${REPO:-$(gh repo view --json nameWithOwner --jq .nameWithOwner)}"

# Comma-separated list of required status check contexts. These names must
# match exactly what GitHub reports — for matrix jobs, include the matrix
# value, e.g. "test-workflows (ubuntu-latest)".
MAIN_REQUIRED_CHECKS="${MAIN_REQUIRED_CHECKS:-test-workflows (ubuntu-latest),Guard main PRs / check-source}"
STAGING_REQUIRED_CHECKS="${STAGING_REQUIRED_CHECKS:-test-workflows (ubuntu-latest)}"

echo "==> Repo: $REPO"

# Build a JSON array of {"context": "..."} from a comma-separated list.
checks_json() {
  local csv="$1"
  jq -nc --arg csv "$csv" '
    $csv | split(",") | map({context: (. | gsub("^\\s+|\\s+$"; ""))})
  '
}

build_ruleset_payload() {
  local name="$1"
  local branch="$2"
  local checks
  checks=$(checks_json "$3")

  jq -nc \
    --arg name "$name" \
    --arg branch "refs/heads/$branch" \
    --argjson checks "$checks" '
    {
      name: $name,
      target: "branch",
      enforcement: "active",
      conditions: {
        ref_name: { include: [$branch], exclude: [] }
      },
      rules: [
        { type: "deletion" },
        { type: "non_fast_forward" },
        {
          type: "pull_request",
          parameters: {
            required_approving_review_count: 0,
            dismiss_stale_reviews_on_push: false,
            require_code_owner_review: false,
            require_last_push_approval: false,
            required_review_thread_resolution: false
          }
        },
        {
          type: "required_status_checks",
          parameters: {
            strict_required_status_checks_policy: false,
            required_status_checks: $checks
          }
        }
      ]
    }'
}

apply_ruleset() {
  local name="$1"
  local payload="$2"

  local existing_id
  existing_id=$(gh api "repos/$REPO/rulesets" \
    --jq ".[] | select(.name == \"$name\") | .id" || true)

  if [ -n "$existing_id" ]; then
    echo "==> Updating ruleset '$name' (id=$existing_id)"
    echo "$payload" | gh api --method PUT "repos/$REPO/rulesets/$existing_id" --input -
  else
    echo "==> Creating ruleset '$name'"
    echo "$payload" | gh api --method POST "repos/$REPO/rulesets" --input -
  fi
}

main_payload=$(build_ruleset_payload "qa-protect-main" "main" "$MAIN_REQUIRED_CHECKS")
staging_payload=$(build_ruleset_payload "qa-protect-staging" "staging" "$STAGING_REQUIRED_CHECKS")

apply_ruleset "qa-protect-main" "$main_payload"
apply_ruleset "qa-protect-staging" "$staging_payload"

echo "==> Done. Verify in: https://github.com/$REPO/settings/rules"
