#! /bin/bash
set -e
f=$(basename $1 uvc)
for ext in HH ; do
    echo rm -rf ${f}$ext.uvc.omni.calfits
    rm -rf ${f}$ext.uvc.omni.calfits
done
