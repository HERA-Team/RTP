#! /bin/bash
set -e

# import common functions
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

if is_lin_pol $1; then
    basename=$(basename $1 uv)
    echo rm -rf ${basename}HH.uv.first.calfits
    rm -rf ${basename}HH.uv.first.calfits
fi
