#!/bin/bash
set -e

# load common functions
source _common.sh

fn=$(basename ${1} uv)

# only upload from linear polarization threads
if is_lin_pol $fn; then
    # get firstcal_metrics filename
    metrics_f=`echo ${fn}HH.uv.firstcal_metrics.json`
    echo add_qm_metrics.py --type=firstcal ${metrics_f}
    add_qm_metrics.py --type=firstcal ${metrics_f}
fi
