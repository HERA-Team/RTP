#! /bin/bash
set -e

# import common functions
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

conn=${1}
store_path=${2}
basename=${3}

fn=$(basename ${basename} uv)

# we only have firstcal files for linear polarizations (e.g., 'xx')
if is_lin_pol $fn; then
    fmetrics_f=`echo ${fn}HH.uv.first.calfits.firstcal_metrics.json`
    total_path=`echo ${store_path}/${fmetrics_f}`
    echo upload_to_librarian.py ${conn} ${fmetrics_f} ${total_path}
    upload_to_librarian.py ${conn} ${fmetrics_f} ${total_path}
fi
