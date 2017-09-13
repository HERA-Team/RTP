#! /bin/bash
set -e

# import common functions
source _common.sh

conn=${1}
store_path=${2}
basename=${3}

fn=$(basename ${basename} uv)

summary_f=`echo ${fn}HH.uvO.flag_summary.npz`
total_path=`echo ${store_path}/${summary_f}`
echo upload_to_librarian.py ${conn} ${summary_f} ${total_path}
upload_to_librarian.py ${conn} ${summary_f} ${total_path}
