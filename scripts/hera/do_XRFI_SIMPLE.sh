#! /bin/bash
set -e

# import common functions
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

# make the file name
bn=$(basename $1 uv)

echo xrfi_run.py --infile_format=miriad --outfile_format=miriad --extension=R --algorithm=xrfi_simple --nsig_dt=6 --nsig_df=6 --nsig_all=0 --summary ${bn}HH.uvO
xrfi_run.py --infile_format=miriad --outfile_format=miriad --extension=R --algorithm=xrfi_simple --nsig_dt=6 --nsig_df=6 --nsig_all=0 --summary ${bn}HH.uvO
