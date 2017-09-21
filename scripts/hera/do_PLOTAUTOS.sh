#! /bin/bash
set -e

# get common functions
source _common.sh

# get basename
fn=$(basename $1 uv)

# define polarizations
pol1="xx"

# only run for first thread
if is_same_pol $fn $pol1; then
    # make wildcard filename
    fn_wc=$(replace_pol $fn "??")

    echo auto_view.py ${fn_wc}uv
    auto_view.py ${fn_wc}uv
fi
