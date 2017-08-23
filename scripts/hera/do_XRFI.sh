#! /bin/bash
set -e

# get useful functions
source _common.sh

# make the file name
bn=$(basename $1 uv)

echo xrfi_run.py --infile_format=miriad --outfile_format=miriad --extension=R --algorithm=xrfi_simple --kt_size=8 --kf_size=8 --sig_init=6 --sig_adj=2 ${bn}HH.uvO
xrfi_run.py --infile_format=miriad --outfile_format=miriad --extension=R --algorithm=xrfi_simple --kt_size=8 --kf_size=8 --sig_init=6 --sig_adj=2 ${bn}HH.uvO
