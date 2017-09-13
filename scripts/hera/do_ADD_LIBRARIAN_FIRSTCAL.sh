#! /bin/bash
set -e

# import common functions
source _common.sh

conn=${1}
store_path=${2}
basename=${3}

fn=$(basename ${basename} uv)

# we only have firstcal files for linear polarizations (e.g., 'xx')
if is_lin_pol $fn; then
    firstcal_f=`echo ${fn}HH.uv.first.calfits`
    total_path=`echo ${store_path}/${firstcal_f}`
    echo upload_to_librarian.py ${conn} ${firstcal_f} ${total_path}
    upload_to_librarian.py ${conn} ${firstcal_f} ${total_path}
fi
