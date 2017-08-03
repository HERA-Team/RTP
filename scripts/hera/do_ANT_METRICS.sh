#! /bin/bash 
set -e
# run script from hera_qm
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

    # make comma-separated list of polarizations
    pols=$(join_by , $pol1 $pol2 $pol3 $pol4)

    echo ant_metrics_run.py -C ${CALBASE} -p $pols --crossCut=5 --deadCut=5 --extension=.ant_metrics.json --vis_format=miriad ${f1}$ext.uvc ${f2}$ext.uvc ${f3}$ext.uvc ${f4}$ext.uvc
    ant_metrics_run.py -C ${CALBASE} -p $pols --crossCut=5 --deadCut=5 --extension=.ant_metrics.json --vis_format=miriad ${f1}$ext.uvc ${f2}$ext.uvc ${f3}$ext.uvc ${f4}$ext.uvc
done
