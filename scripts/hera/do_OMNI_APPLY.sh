#! /bin/bash
set -e

f1=$(basename $1 uvc)
f2=$(basename $2 uvc)
f3=$(basename $3 uvc)
f4=$(basename $4 uvc)

# function for concatenating strings
# from https://stackoverflow.com/questions/1527049/join-elements-of-an-array
# example syntax: (join_by , a b c) -> a,b,c
function join_by { local IFS="$1"; shift; echo "$*"; }

for ext in HH ; do
    pol1=$(echo $f1 | sed -e 's/.*\.\(..\)\.$/\1/')
    pol2=$(echo $f2 | sed -e 's/.*\.\(..\)\.$/\1/')
    pol3=$(echo $f3 | sed -e 's/.*\.\(..\)\.$/\1/')
    pol4=$(echo $f4 | sed -e 's/.*\.\(..\)\.$/\1/')

    # make comma-separated list of polarizations
    pols=$(join_by , $pol1 $pol2 $pol3 $pol4)

    # get the name of the omnical file
    nopol_base=$(echo $f1 | sed -e "s/\.${pol1}\././")
    omni_f=`echo ${nopol_base}.omni.calfits`

    echo omni_apply.py -p $pols --omnipath=$omni_f --extension=O ${f1}$ext.uvc ${f2}$ext.uvc ${f3}$ext.uvc ${f4}$ext.uvc
    omni_apply.py -p $pols --omnipath=$omni_f --extension=O ${f1}$ext.uvc ${f2}$ext.uvc ${f3}$ext.uvc ${f4}$ext.uvc
done
