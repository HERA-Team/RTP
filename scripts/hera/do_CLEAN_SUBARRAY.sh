#! /bin/bash
set -e
f=$(basename $1 uvc)
echo ${f}
for ext in HH ; do
    echo rm -rf ${f}$ext.uvc
    rm -rf ${f}$ext.uvc
done
