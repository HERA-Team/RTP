#! /bin/bash
set -e

# import common functions
source _common.sh

conn=${1}
store_path=${2}
basename=${3}

# get base file name
bn=$(basename ${basename} uv)

filename=`echo ${bn}HH.uvOR`
total_path=`echo ${store_path}/${filename}`
echo upload_to_librarian.py ${conn} ${filename} ${total_path}
upload_to_librarian.py ${conn} ${filename} ${total_path}

# also add flag summary
filename=`echo ${bn}HH.uvO.flag_summary.npz`
total_path=`echo ${store_path}/${filename}`
echo upload_to_librarian.py ${conn} ${filename} ${total_path}
upload_to_librarian.py ${conn} ${filename} ${total_path}
