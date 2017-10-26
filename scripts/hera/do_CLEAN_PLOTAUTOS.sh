#! /bin/bash
set -e

# import common functions
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

# define polarization
pol1="xx"

# get basename
fn=$(basename "$1" uv)

# only run deletion from the main thread
if is_same_pol $fn $pol1; then
    # get output filenames
    nopol_base=$(remove_pol $fn)
    autos=`echo ${nopol_base}auto_specs.png`
    pos=`echo ${nopol_base}auto_v_pos.png`
    rxr=`echo ${nopol_base}auto_v_rxr.png`
    rmsx=`echo ${nopol_base}xx.auto_rms_values.png`
    rmsy=`echo ${nopol_base}yy.auto_rms_values.png`

    rm -rf ${autos}
    rm -rf ${pos}
    rm -rf ${rxr}
    rm -rf ${rmsx}
    rm -rf ${rmsy}
fi
