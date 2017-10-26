#! /bin/bash
set -e

# import common functions
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

# define polarization
pol1="xx"

basename=$(basename $1 uv)
echo rm -rf ${basename}HH.uvOR
rm -rf ${basename}HH.uvOR
echo rm -rf ${basename}HH.uvO.flag_summary.npz
rm -rf ${basename}HH.uvO.flag_summary.npz
echo rm -rf ${basename}HH.uvO.flags.npz
rm -rf ${basename}HH.uvO.flags.npz
if is_same_pol ${basename} ${pol1}; then
    nopol_base=$(remove_pol $basename)
    echo rm -rf ${nopol_base}HH.uv.vis.uvfits.flags.npz
    rm -rf ${nopol_base}HH.uv.vis.uvfits.flags.npz
    echo rm -rf ${nopol_base}HH.uv.omni.calfits.x.flags.npz
    rm -rf ${nopol_base}HH.uv.omni.calfits.x.flags.npz
    echo rm -rf ${nopol_base}HH.uv.omni.calfits.g.flags.npz
    rm -rf ${nopol_base}HH.uv.omni.calfits.g.flags.npz
fi
