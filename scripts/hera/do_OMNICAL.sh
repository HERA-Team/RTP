#! /bin/bash
set -e

CALBASE=hsa7458_v001
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

    # get metrics file name
    nopol_base=$(echo $f1 | sed -e "s/\.${pol1}\././")
    metrics_f=`echo ${nopol_base}.metrics.json`

    # get firstcal file names
    # should be auto-pol (e.g., 'xx')
    declare -a FCAL_ARR
    idx=0
    for pol in $pol1 $pol2 $pol3 $pol4; do
	# test to see if both characters match
	if [ ${pol:0:1} == ${pol:1:1} ]; then
	    # if they match, add them to array
	    FCAL_ARR[$idx]=$pol
	    idx=$((idx+1))
	fi
    done

    # make list of firstcal files by iterating over array values
    idx=0
    for pol in "${FCAL_ARR[@]}"; do
	base=$(echo $f1 | sed -e "s/.*\.\(..\)\.$/${pol}/")
	FCAL_ARR[$idx]=`echo ${base}.uvc.first.calfits`
	idx=$((idx+1))
    done

    # make comma-separated list of firstcal files
    fcal=$(join_by , "${FCAL_ARR[@]}")

    # make comma-separated list of polarizations
    pols=$(join_by , $pol1 $pol2 $pol3 $pol4)

    echo omni_run.py -C ${CALBASE} --metrics_json=$metrics_f --firstcal=$fcal -p $pols ${f1}$ext.uvc ${f2}$ext.uvc ${f3}$ext.uvc ${f4}$ext.uvc
    omni_run.py -C ${CALBASE} --metrics_json=$metrics_f --firstcal=$fcal -p $pols ${f1}$ext.uvc ${f2}$ext.uvc ${f3}$ext.uvc ${f4}$ext.uvc
done
