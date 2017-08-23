#! /bin/bash
set -e

# import common functions
source _common.sh

conn=${1}
store_path=${2}
basename=${3}

fn=$(basename ${basename} uv)

xmetrics_f=`echo ${fn}HH.uv.xrfi_metrics.npz`
total_path=`echo ${store_path}/${xmetrics_f}`
echo upload_to_librarian.py ${conn} ${xmetrics_f} ${total_path}
upload_to_librarian.py ${conn} ${xmetrics_f} ${total_path}
