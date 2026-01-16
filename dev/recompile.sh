#!/bin/bash

shift
flags=$*

pixi update --manifest-path pixi.toml -e compile

# (re)initialize dot executable to ensure graphviz is available
pixi run --manifest-path pixi.toml -e compile dot -c

echo "recompiling spec.yaml with flags '--clobber ${flags}'"

command="pixi run --manifest-path pixi.toml -e compile \
ecoscope-workflows compile --spec spec.yaml --clobber ${flags}"

exec $command
