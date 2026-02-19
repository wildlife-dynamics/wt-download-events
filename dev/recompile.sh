#!/bin/bash

# Parse flags: --local is consumed by the script, everything else passed to compiler
local_mode=false
compiler_flags=()
for arg in "$@"; do
    case $arg in
        --local) local_mode=true ;;
        *) compiler_flags+=("$arg") ;;
    esac
done
flags="${compiler_flags[*]}"

# Helper to run commands with or without pixi
run_cmd() {
    if [ "$local_mode" = true ]; then
        "$@"
    else
        pixi run --manifest-path pixi.toml -e compile "$@"
    fi
}

# Derive generated directory from spec.yaml id field
WORKFLOW_ID=$(grep '^id:' spec.yaml | sed 's/^id: *//' | tr '_' '-')
GENERATED_DIR="ecoscope-workflows-${WORKFLOW_ID}-workflow"

# Stash pixi.lock and VERSION.yaml before clobber (if they exist)
STASH_DIR=$(mktemp -d)
[ -f "${GENERATED_DIR}/pixi.lock" ] && cp "${GENERATED_DIR}/pixi.lock" "${STASH_DIR}/pixi.lock"
[ -f "${GENERATED_DIR}/VERSION.yaml" ] && cp "${GENERATED_DIR}/VERSION.yaml" "${STASH_DIR}/VERSION.yaml"

if [ "$local_mode" = false ]; then
    pixi update --manifest-path pixi.toml -e compile
fi

# (re)initialize dot executable to ensure graphviz is available
run_cmd dot -c

echo "recompiling spec.yaml with flags '--clobber ${flags}'"

run_cmd ecoscope-workflows compile --spec spec.yaml --clobber ${flags}
compile_exit=$?

# Restore stashed files only if the compiler didn't produce them
if [ -f "${STASH_DIR}/pixi.lock" ] && [ ! -f "${GENERATED_DIR}/pixi.lock" ]; then
    cp "${STASH_DIR}/pixi.lock" "${GENERATED_DIR}/pixi.lock"
    echo "Restored pixi.lock from stash"
fi
if [ -f "${STASH_DIR}/VERSION.yaml" ] && [ ! -f "${GENERATED_DIR}/VERSION.yaml" ]; then
    cp "${STASH_DIR}/VERSION.yaml" "${GENERATED_DIR}/VERSION.yaml"
    echo "Restored VERSION.yaml from stash"
fi

rm -rf "${STASH_DIR}"
exit $compile_exit
