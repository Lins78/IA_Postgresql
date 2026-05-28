#!/usr/bin/env bash
SCRIPT_DIR=$(cd $(dirname ${BASH_SOURCE[0]}") && pwd)/scripts/linux
exec "$SCRIPT_DIR/run.sh $@

