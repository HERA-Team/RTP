#! /bin/bash
set -e

# get common functions
source _common.sh

if is_lin_pol $1; then
    basename=$(basename $1 uv)
    echo rm -rf ${basename}HH.uv.first.calfits.firstcal_metrics.json
    rm -rf ${basename}HH.uv.first.calfits.firstcal_metrics.json
fi
