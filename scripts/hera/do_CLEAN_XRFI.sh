#! /bin/bash
set -e

# get common functions
source _common.sh

basename=$(basename $1 uv)
echo rm -rf ${basename}HH.uvOR
rm -rf ${basename}HH.uvOR
