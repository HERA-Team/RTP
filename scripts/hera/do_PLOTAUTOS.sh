#! /bin/bash
set -e

# import common functions
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

# get basename
fn=$(basename $1 uv)

# define polarizations of interest
pol1="xx"
pol2="yy"

# only run for first thread
if is_same_pol $fn $pol1; then
    # make desired filenames
    fn_xx=$(replace_pol $fn $pol1)
    fn_yy=$(replace_pol $fn $pol2)

    echo auto_view.py ${fn_xx}uv ${fn_yy}uv
    auto_view.py ${fn_xx}uv ${fn_yy}uv
fi
