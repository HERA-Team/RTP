#! /bin/bash
set -e
CALBASE=hsa7458_v001
#CALFILE_HH=hsa7458_v000_HH.py #hsa7458_v000
#CALFILE_PH=hsa7458_v000_PH.py #psa...

f=$(basename $1 uvc)

for ext in HH ; do
    pol=$(echo $f |sed -e 's/.*\.\(..\)\.$/\1/')
    nopol_base=$(echo $f | sed -e "s/\.${pol}\././")
    metrics_f=`echo ${nopol_base}.metrics.json`
    echo firstcal_run.py -C ${CALBASE} --metrics_json=$metrics_f --pol=$pol ${f}$ext.uvc
    firstcal_run.py -C ${CALBASE} --metrics_json=$metrics_f --pol=$pol ${f}$ext.uvc
done

