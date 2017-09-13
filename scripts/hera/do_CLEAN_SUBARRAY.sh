#! /bin/bash
set -e
f=$(basename $1 uv)
echo ${f}

echo rm -rf ${f}HH.uv
rm -rf ${f}HH.uv
