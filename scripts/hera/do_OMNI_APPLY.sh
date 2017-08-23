#! /bin/bash
set -e

# load common funcitons
source _common.sh

# get base filename
fn=$(basename $1 uv)

# get polarization
pol=$(get_pol $fn)

# get the name of the omnical file
nopol_base=$(remove_pol $fn)
omni_f=`echo ${nopol_base}HH.uv.omni.calfits`

echo omni_apply.py -p $pol --omnipath=$omni_f --extension=O ${fn}HH.uv
omni_apply.py -p $pol --omnipath=$omni_f --extension=O ${fn}HH.uv
