#! /bin/bash
set -e

# import functions
source _common.sh

fn=$(basename $1 uv)

# we only want to run firstcal on linear polarizations (e.g. "xx")
if is_lin_pol $fn; then
    pol=$(get_pol $fn)
    nopol_base=$(remove_pol $fn)
    metrics_f=`echo ${nopol_base}HH.uv.ant_metrics.json`
    echo firstcal_run.py --metrics_json=$metrics_f --pol=$pol ${fn}HH.uv
    firstcal_run.py --metrics_json=$metrics_f --pol=$pol ${fn}HH.uv
fi
