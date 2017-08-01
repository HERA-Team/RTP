#! /bin/bash
set -e

echo xrfi_run.py --infile_format=miriad --outfile_format=miriad --extension=R --algorithm=xrfi --kt_size=8 --kf_size=8 --sig_init=6 --sig_adj=2 $1
xrfi_run.py --infile_format=miriad --outfile_format=miriad --extension=R --algorithm=xrfi --kt_size=8 --kf_size=8 --sig_init=6 --sig_adj=2 $1
