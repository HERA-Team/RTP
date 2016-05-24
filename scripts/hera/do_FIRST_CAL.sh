#! /bin/bash

CALFILE=hsa7458_v000

bad_ant_file=$1.bad_ants
bad_ants = `cat ${bad_ant_file}`
firstcal.py -C ${CALFILE} --ex_ants=${bad_ants} $1


