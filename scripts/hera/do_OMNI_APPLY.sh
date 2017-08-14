#! /bin/bash
set -e

# load common funcitons
source _common.sh

# get base filename
fn=$(basename $1 uvc)

# get polarization
pol=$(get_pol $fn)

# get the name of the omnical file
nopol_base=$(remove_pol $fn)
omni_f=`echo ${nopol_base}HH.uvc.omni.calfits`

echo omni_apply.py -p $pol --omnipath=$omni_f --extension=O ${fn}HH.uvc
omni_apply.py -p $pol --omnipath=$omni_f --extension=O ${fn}HH.uvc
