#! /bin/bash
set -e
CALFILE_HH=XXX #hsa7458_v000
CALFILE_PH=XXX #psa...

f=$(basename $1 uvc)
bad_ant_file=$1.bad_ants
bad_ants = `cat ${bad_ant_file}`

for ext in HH PH
    do
        echo firstcal.py -C ${CALFILE} --ex_ants=${bad_ants} ${f}$ext.uvc 
        firstcal.py -C ${CALFILE} --ex_ants=${bad_ants} ${f}$ext.uvc 
done

