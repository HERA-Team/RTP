#! /bin/bash
set -e

# get common functions
source _common.sh

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
    rms=`echo ${nopol_base}auto_rms_values.png`

    rm -rf ${autos}
    rm -rf ${pos}
    rm -rf ${rxr}
    rm -rf ${rms}
fi
