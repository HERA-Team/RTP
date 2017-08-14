#! /bin/bash
set -e

# get common functions
source _common.sh

# define base polarization
pol1="xx"

if is_same_pol $1 $pol1; then
    # get base filename
    base_fn=$(remove_pol $1)
    echo rm -rf ${base_fn}.omni.calfits
    rm -rf ${base_fn}.omni.calfits
done
