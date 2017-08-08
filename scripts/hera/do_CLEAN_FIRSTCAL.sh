#! /bin/bash
set -e

# get common functions
source _common.sh

if is_lin_pol $1; then
    echo rm -rf ${1}.first.calfits
    rm -rf ${1}.first.calfits
fi
