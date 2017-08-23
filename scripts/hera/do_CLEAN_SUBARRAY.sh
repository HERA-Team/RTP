#! /bin/bash
set -e
f=$(basename $1 uv)
echo ${f}
for ext in HH ; do
    echo rm -rf ${f}$ext.uv
    rm -rf ${f}$ext.uv
done
