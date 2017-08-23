#! /bin/bash
set -e

# import functions
source _common.sh

fn=$(basename $1 uv)

# we only want to run firstcal on linear polarizations (e.g. "xx")
if is_lin_pol $fn; then
    metrics_f=`echo ${fn}HH.uvc.first.calfits`
    echo firstcal_metrics_run.py --std_cut=0.5 --extension=.firstcal_metrics.json ${metrics_f}
    firstcal_metrics_run.py --std_cut=0.5 --extension=.firstcal_metrics.json ${metrics_f}
fi
