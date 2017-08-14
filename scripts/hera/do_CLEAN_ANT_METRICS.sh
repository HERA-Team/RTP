#! /bin/bash
set -e

# import common functions
source _common.sh

# we only want to run this script for "xx" polarization
pol1="xx"

if is_same_pol $1 $pol1; then
    # get base file name
    base_fn=$(remove_pol $1)
    echo rm -rf ${base_fn}.ant_metrics.json
    rm -rf $1 ${base_fn}.ant_metrics.json
fi
