#! /bin/bash
set -e

# import common functions
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

basename=$(basename $1 uv)
echo rm -rf ${basename}HH.uvO
rm -rf ${basename}HH.uvO
