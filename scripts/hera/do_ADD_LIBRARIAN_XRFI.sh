#! /bin/bash
set -e

# import common functions
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

conn=${1}
store_path=${2}
basename=${3}

pol1="xx"

# get base file name
bn=$(basename ${basename} uv)

# upload flagged visibility file
filename=`echo ${bn}HH.uvOR`
total_path=`echo ${store_path}/${filename}`
echo upload_to_librarian.py ${conn} ${filename} ${total_path}
upload_to_librarian.py ${conn} ${filename} ${total_path}

# also add flag summary
filename=`echo ${bn}HH.uvO.flag_summary.npz`
total_path=`echo ${store_path}/${filename}`
echo upload_to_librarian.py ${conn} ${filename} ${total_path}
upload_to_librarian.py ${conn} ${filename} ${total_path}

# add raw visibility waterfalls
filename=`echo ${bn}HH.uvO.flags.npz`
total_path=`echo ${store_path}/${filename}`
echo upload_to_librarian.py ${conn} ${filename} ${total_path}
upload_to_librarian.py ${conn} ${filename} ${total_path}

if is_same_pol ${bn} ${pol1}; then
    # add extra waterfalls
    nopol_base=$(remove_pol ${bn})
    vis_wf=`echo ${nopol_base}HH.uv.vis.uvfits.flags.npz`
    chi_wf=`echo ${nopol_base}HH.uv.omni.calfits.x.flags.npz`
    g_wf=`echo ${nopol_base}HH.uv.omni.calfits.g.flags.npz`

    # upload to librarian
    total_path=`echo ${store_path}/${vis_wf}`
    echo upload_to_librarian.py ${conn} ${vis_wf} ${total_path}
    upload_to_librarian.py ${conn} ${vis_wf} ${total_path}
    total_path=`echo ${store_path}/${chi_wf}`
    echo upload_to_librarian.py ${conn} ${chi_wf} ${total_path}
    upload_to_librarian.py ${conn} ${chi_wf} ${total_path}
    total_path=`echo ${store_path}/${g_wf}`
    echo upload_to_librarian.py ${conn} ${g_wf} ${total_path}
    upload_to_librarian.py ${conn} ${g_wf} ${total_path}
fi
