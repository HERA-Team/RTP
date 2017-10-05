#! /bin/bash
set -e

# get common functions
source _common.sh

# define base polarization
pol1="xx"

basename=$(basename ${1} uv)

if is_same_pol $1 $pol1; then
    # get base filename
    nopol_base=$(remove_pol ${basename})
    echo rm -rf ${nopol_base}HH.uv.omni.calfits
    rm -rf ${nopol_base}HH.uv.omni.calfits
    echo rm -rf ${nopol_base}HH.uv.vis.uvfits
    rm -rf ${nopol_base}HH.uv.vis.uvfits
    echo rm -rf ${nopol_base}HH.uv.xtalk.uvfits
    rm -rf ${nopol_base}HH.uv.xtalk.uvfits
fi
