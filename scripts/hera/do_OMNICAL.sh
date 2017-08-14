#! /bin/bash
set -e

# load common funcitons
source _common.sh

CALBASE=hsa7458_v001
fn=$(basename $1 uvc)

# define polarizations
pol1="xx"
pol2="yy"
pol3="xy"
pol4="yx"

# we only run omnical for the base filename
if is_same_pol $fn $pol1; then
    # get metrics file name
    nopol_base=$(remove_pol $fn)
    metrics_f=`echo ${nopol_base}HH.uvc.ant_metrics.json`

    # define polarization file names
    fn1=$(replace_pol $fn $pol1)
    fn2=$(replace_pol $fn $pol2)
    fn3=$(replace_pol $fn $pol3)
    fn4=$(replace_pol $fn $pol4)

    # get firstcal file names
    # should be auto-pol (e.g., 'xx')
    declare -a FCAL_ARR
    idx=0
    for f in $fn1 $fn2 $fn3 $fn4; do
	# test if file is a linear polarization
	if is_lin_pol $f; then
	    # add to array
	    file_pol=$(get_pol $f)
	    FCAL_ARR[$idx]=$file_pol
	    idx=$((idx+1))
	fi
    done

    # make list of firstcal files by iterating over array values
    idx=0
    for pol in "${FCAL_ARR[@]}"; do
	base=$(replace_pol $fn $pol)
	FCAL_ARR[$idx]=`echo ${base}HH.uvc.first.calfits`
	idx=$((idx+1))
    done

    # make comma-separated list of firstcal files
    fcal=$(join_by , "${FCAL_ARR[@]}")

    # make comma-separated list of polarizations
    pols=$(join_by , $pol1 $pol2 $pol3 $pol4)

    echo omni_run.py -C ${CALBASE} --metrics_json=$metrics_f --firstcal=$fcal -p $pols ${fn1}HH..uvc ${fn2}HH.uvc ${fn3}HH.uvc ${fn4}HH.uvc
    omni_run.py -C ${CALBASE} --metrics_json=$metrics_f --firstcal=$fcal -p $pols ${fn1}HH.uvc ${fn2}HH.uvc ${fn3}HH.uvc ${fn4}HH.uvc
fi
